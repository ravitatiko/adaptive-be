from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Optional
import logging
import google.generativeai as genai
from datetime import datetime
from app.core.config import settings
from app.core.mongodb import get_database
# Visual cues are text-based, no service needed
from app.schemas.content_transformer import (
    ContentTransformerRequest,
    ContentTransformerResponse,
    ContentTransformerError
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Configure Google Generative AI
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    logger.warning("Google API key not configured")

@router.post(
    "/transform",
    response_model=ContentTransformerResponse,
    status_code=status.HTTP_200_OK,
    summary="Transform Content",
    description="Transform content into storytelling, visual_cue, and summary modes based on domain and hobby.",
    responses={
        200: {
            "description": "Content transformed successfully",
            "model": ContentTransformerResponse
        },
        400: {
            "description": "Bad request - invalid input",
            "model": ContentTransformerError
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def transform_content(request: ContentTransformerRequest, db=Depends(get_database)):
    """
    Transform content based on the selected style, domain, and hobby, then save to database.
    
    - **assetCode**: Asset code identifier
    - **style**: Transformation style (storytelling, visual_cue, or summary)
    - **content**: Raw content to transform (lecture, case study, or concept)
    - **domain**: Domain context (e.g., Business, Engineering, Medicine, Education)
    - **hobby**: Hobby context (e.g., Movies, Cricket, Gaming, Music)
    
    Returns transformed content and saves it to the transformed-assets collection.
    """
    try:
        logger.info(f"Transforming content for assetCode: {request.assetCode}, style: {request.style}, domain: {request.domain}, hobby: {request.hobby}")
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Generative AI not configured. Please check API key."
            )
        
        # Create style-specific prompts
        style_prompts = {
            "storytelling": """
### Storytelling Mode:
- Convert the given content into a short storytelling analogy.
- Make it relevant to the given domain and hobby.
- Use simple, engaging language.
- Create a narrative that helps explain the concept through a relatable story.
""",
          "visual_cue": """
### Visual Cue Mode:
- Convert the content into simple, symbolic visual representations (emoji flows, ASCII diagrams, metaphors).
- Focus on clarity, simplicity, and instant understanding at a glance.
- Provide 3–4 different cues for the same concept.
- Each visual cue must connect the concept to the user's domain and hobby.
- Use emojis, arrows, or short symbolic flows instead of long text.
- Keep it fun, relatable, and visually intuitive.

Format your response as:
VISUAL CUE 1: [Emoji flow or diagram]
VISUAL CUE 2: [Emoji flow or diagram]
VISUAL CUE 3: [Emoji flow or diagram]
VISUAL CUE 4: [Optional extra if needed]
""",
            "summary": """
### Summary Mode:
- Generate a concise summary of the content.
- Keep it framed in the context of the given domain and hobby.
- Make it clear, informative, and easy to understand.
- Use analogies from the hobby to explain domain concepts.
""",
            "original": """
### Original Mode:
- Return the content as-is without any transformation.
- This is the original learning material in its basic form.
- No domain or hobby contextualization needed.
"""
        }
        
        # Handle original style without AI transformation
        if request.style == "original":
            output = request.content
        else:
            # Create the AI prompt based on selected style
            prompt = f"""You are an AI content transformer. 
You will receive four inputs:
1. Style (storytelling, visual_cue, or summary)
2. Content (raw lecture, case study, or concept)
3. Domain (e.g., Business, Engineering, Medicine, Education, etc.)
4. Hobby (e.g., Movies, Cricket, Gaming, Music, etc.)

Your task is to generate content in the specified style:

{style_prompts[request.style]}

### Examples for {request.style.title()} Mode:

**Content:** "Neural networks learn patterns from data."
**Domain:** Business
**Hobby:** Cricket

**Storytelling Mode Example:** 
"Imagine a cricket coach who studies thousands of player stats (data) to predict the best batting order. That's how neural networks learn patterns to make predictions."

**Visual Cue Mode Example:** 
VISUAL CUE 1: 🏏📊➡️🧠➡️🎯 (Cricket data → Neural Network → Target prediction)
VISUAL CUE 2: 📈📋➡️🤖➡️💼 (Business charts → AI brain → Better decisions)  
VISUAL CUE 3: Data ➡️ NN ➡️ Pattern ➡️ 🏆 (Linear flow to success)
VISUAL CUE 4: 🧠=🏏coach (Neural Network equals cricket coach analogy)

**Summary Mode Example:** 
"Neural networks are like a cricket coach for business — analyzing tons of data to spot patterns and make smarter predictions."

---

Now transform this content in {request.style} style:

**Style:** {request.style}
**Content:** "{request.content}"
**Domain:** {request.domain}
**Hobby:** {request.hobby}

Please provide ONLY the {request.style} output without any formatting or labels:"""

            # Generate response using Google Generative AI
            response = model.generate_content(prompt)
            
            if not response.text:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate content transformation"
                )
            
            # Parse the response - since we asked for only the output, use it directly
            output = response.text.strip()
        
        # Clean up any unwanted formatting
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1]
        
        # Visual cues are text-based, no image generation needed
        visual_cue_data = None
        
        # Prepare data for insertion into assets collection
        # content field stores the generated content (not original)
        from bson import ObjectId
        
        # Convert assetCode to ObjectId if it's a valid ObjectId string
        try:
            code_as_objectid = ObjectId(request.assetCode)
        except Exception:
            # If not a valid ObjectId, keep as string
            code_as_objectid = request.assetCode
        
        asset_data = {
            "code": code_as_objectid,
            "content": output,  # Generated content goes in content field
            "style": request.style,
            "domain": request.domain,
            "hobby": request.hobby,
            "created_at": datetime.utcnow()
        }
        
        # Visual cues are text-based only, no image data to add
        
        # Insert into MongoDB assets collection only
        asset_result = await db["assets"].insert_one(asset_data)
        
        if not asset_result.inserted_id:
            logger.error("Failed to insert data into assets collection")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save data to database"
            )
        
        logger.info(f"Successfully transformed and saved content for assetCode: {request.assetCode}, style: {request.style}")
        logger.info(f"Asset ID: {asset_result.inserted_id}")
        
        return ContentTransformerResponse(
            id=str(asset_result.inserted_id),
            assetCode=request.assetCode,
            style=request.style,
            output=output,
            original_content="",  # Not storing original content anymore
            domain=request.domain,
            hobby=request.hobby,
            created_at=asset_data["created_at"].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transforming content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transform content: {str(e)}"
        )

@router.get(
    "/get-or-generate",
    response_model=ContentTransformerResponse,
    summary="Get or Generate Transformed Content",
    description="Check if transformed content exists for the combination (assetCode, style, domain, hobby). If exists, return it; otherwise generate and save new content."
)
async def get_or_generate_content(
    assetCode: str,
    style: str,
    content: str,
    domain: str,
    hobby: str,
    db=Depends(get_database)
):
    """
    Get existing transformed content or generate new content if not found.
    
    - **assetCode**: Asset code identifier
    - **style**: Transformation style (storytelling, visual_cue, or summary)
    - **content**: Raw content to transform (used only if generating new content)
    - **domain**: Domain context
    - **hobby**: Hobby context
    
    Returns existing content if found, otherwise generates and saves new content.
    """
    try:
        logger.info(f"Checking for existing content: assetCode={assetCode}, style={style}, domain={domain}, hobby={hobby}")
        
        # Check if record already exists with the same combination
        from bson import ObjectId
        
        # Try to convert assetCode to ObjectId for search
        try:
            search_code = ObjectId(assetCode)
        except Exception:
            # If not a valid ObjectId, search as string
            search_code = assetCode
        
        existing_record = await db["transformed-assets"].find_one({
            "assetCode": search_code,
            "style": style,
            "domain": domain,
            "hobby": hobby
        })
        
        if existing_record:
            # Record exists, return it
            logger.info(f"Found existing record for assetCode: {assetCode}")
            existing_record["id"] = str(existing_record["_id"])
            del existing_record["_id"]
            
            return ContentTransformerResponse(
                id=existing_record["id"],
                assetCode=existing_record["assetCode"],
                style=existing_record["style"],
                output=existing_record["content"],
                original_content=existing_record["original_content"],
                domain=existing_record["domain"],
                hobby=existing_record["hobby"],
                created_at=existing_record["created_at"].isoformat()
            )
        
        # Record doesn't exist, generate new content
        logger.info(f"No existing record found, generating new content for assetCode: {assetCode}")
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Generative AI not configured. Please check API key."
            )
        
        # Create style-specific prompts
        style_prompts = {
            "storytelling": """
### Storytelling Mode:
- Convert the given content into a short storytelling analogy.
- Make it relevant to the given domain and hobby.
- Use simple, engaging language.
- Create a narrative that helps explain the concept through a relatable story.
""",
            "visual_cue": """
### Visual Cue Mode:
- Convert the content into simple, symbolic visual representations (emoji flows, ASCII diagrams, metaphors).
- Focus on clarity, simplicity, and instant understanding at a glance.
- Provide 3–4 different cues for the same concept.
- Each visual cue must connect the concept to the user's domain and hobby.
- Use emojis, arrows, or short symbolic flows instead of long text.
- Keep it fun, relatable, and visually intuitive.

Format your response as:
VISUAL CUE 1: [Emoji flow or diagram]
VISUAL CUE 2: [Emoji flow or diagram]
VISUAL CUE 3: [Emoji flow or diagram]
VISUAL CUE 4: [Optional extra if needed]
""",
            "summary": """
### Summary Mode:
- Generate a concise summary of the content.
- Keep it framed in the context of the given domain and hobby.
- Make it clear, informative, and easy to understand.
- Use analogies from the hobby to explain domain concepts.
"""
        }
        
        # Create the AI prompt based on selected style
        prompt = f"""You are an AI content transformer. 
You will receive four inputs:
1. Style (storytelling, visual_cue, or summary)
2. Content (raw lecture, case study, or concept)
3. Domain (e.g., Business, Engineering, Medicine, Education, etc.)
4. Hobby (e.g., Movies, Cricket, Gaming, Music, etc.)

Your task is to generate content in the specified style:

{style_prompts.get(style, style_prompts["summary"])}

### Examples for {style.title()} Mode:

**Content:** "Neural networks learn patterns from data."
**Domain:** Business
**Hobby:** Cricket

**Storytelling Mode Example:** 
"Imagine a cricket coach who studies thousands of player stats (data) to predict the best batting order. That's how neural networks learn patterns to make predictions."

**Visual Cue Mode Example:** 
VISUAL CUE 1: 🏏📊➡️🧠➡️🎯 (Cricket data → Neural Network → Target prediction)
VISUAL CUE 2: 📈📋➡️🤖➡️💼 (Business charts → AI brain → Better decisions)  
VISUAL CUE 3: Data ➡️ NN ➡️ Pattern ➡️ 🏆 (Linear flow to success)
VISUAL CUE 4: 🧠=🏏coach (Neural Network equals cricket coach analogy)

**Summary Mode Example:** 
"Neural networks are like a cricket coach for business — analyzing tons of data to spot patterns and make smarter predictions."

---

Now transform this content in {style} style:

**Style:** {style}
**Content:** "{content}"
**Domain:** {domain}
**Hobby:** {hobby}

Please provide ONLY the {style} output without any formatting or labels:"""

        # Generate response using Google Generative AI
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate content transformation"
            )
        
        # Parse the response
        output = response.text.strip()
        
        # Clean up any unwanted formatting
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1]
        
        # Prepare data for insertion into transformed-assets collection
        from bson import ObjectId
        
        # Convert assetCode to ObjectId if it's a valid ObjectId string
        try:
            code_as_objectid = ObjectId(assetCode)
        except Exception:
            # If not a valid ObjectId, keep as string
            code_as_objectid = assetCode
        
        transformed_asset = {
            "assetCode": code_as_objectid,
            "style": style,
            "content": output,
            "original_content": content,
            "domain": domain,
            "hobby": hobby,
            "created_at": datetime.utcnow()
        }
        
        # Insert into MongoDB transformed-assets collection
        result = await db["transformed-assets"].insert_one(transformed_asset)
        
        if not result.inserted_id:
            logger.error("Failed to insert transformed content into database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save transformed content to database"
            )
        
        logger.info(f"Successfully generated and saved new content for assetCode: {assetCode}")
        
        return ContentTransformerResponse(
            id=str(result.inserted_id),
            assetCode=assetCode,
            style=style,
            output=output,
            original_content=content,
            domain=domain,
            hobby=hobby,
            created_at=transformed_asset["created_at"].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_or_generate_content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get or generate content: {str(e)}"
        )

@router.get(
    "/assets/{asset_code}",
    summary="Get Transformed Assets by Asset Code",
    description="Retrieve all transformed assets for a specific asset code."
)
async def get_transformed_assets(asset_code: str, db=Depends(get_database)):
    """Get all transformed assets for a specific asset code"""
    try:
        logger.info(f"Fetching transformed assets for asset code: {asset_code}")
        
        # Find all transformed assets for the given asset code
        assets_cursor = db["transformed-assets"].find({"assetCode": asset_code})
        assets = await assets_cursor.to_list(length=None)
        
        # Convert MongoDB ObjectIds to strings
        for asset in assets:
            asset["id"] = str(asset["_id"])
            del asset["_id"]
            if "created_at" in asset and hasattr(asset["created_at"], 'isoformat'):
                asset["created_at"] = asset["created_at"].isoformat()
        
        logger.info(f"Found {len(assets)} transformed assets for asset code: {asset_code}")
        return {
            "assetCode": asset_code,
            "count": len(assets),
            "assets": assets
        }
        
    except Exception as e:
        logger.error(f"Error fetching transformed assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transformed assets: {str(e)}"
        )

@router.get(
    "/assets-collection",
    summary="Get All Assets from Assets Collection",
    description="Retrieve all assets from the assets collection."
)
async def get_all_assets(db=Depends(get_database)):
    """Get all assets from assets collection"""
    try:
        logger.info("Fetching all assets from assets collection")
        
        # Find all assets
        assets_cursor = db["assets"].find({})
        assets = await assets_cursor.to_list(length=None)
        
        # Convert MongoDB ObjectIds to strings and handle all fields properly
        for asset in assets:
            if "_id" in asset:
                asset["id"] = str(asset["_id"])
                del asset["_id"]
            if "created_at" in asset and hasattr(asset["created_at"], 'isoformat'):
                asset["created_at"] = asset["created_at"].isoformat()
            
            # Convert any ObjectId fields to strings
            for key, value in list(asset.items()):
                if hasattr(value, 'generation_time'):  # Check if it's an ObjectId
                    asset[key] = str(value)
        
        logger.info(f"Found {len(assets)} total assets")
        return {
            "count": len(assets),
            "assets": assets
        }
        
    except Exception as e:
        logger.error(f"Error fetching all assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch assets: {str(e)}"
        )

@router.get(
    "/assets",
    summary="Get All Transformed Assets",
    description="Retrieve all transformed assets from the database."
)
async def get_all_transformed_assets(db=Depends(get_database)):
    """Get all transformed assets"""
    try:
        logger.info("Fetching all transformed assets")
        
        # Find all transformed assets
        assets_cursor = db["transformed-assets"].find({})
        assets = await assets_cursor.to_list(length=None)
        
        # Convert MongoDB ObjectIds to strings
        for asset in assets:
            asset["id"] = str(asset["_id"])
            del asset["_id"]
            if "created_at" in asset and hasattr(asset["created_at"], 'isoformat'):
                asset["created_at"] = asset["created_at"].isoformat()
        
        logger.info(f"Found {len(assets)} total transformed assets")
        return {
            "count": len(assets),
            "assets": assets
        }
        
    except Exception as e:
        logger.error(f"Error fetching all transformed assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transformed assets: {str(e)}"
        )


@router.get(
    "/getAsset",
    summary="Get Asset with Default Original Fallback", 
    description="Get asset by code, domain, hobby, and style. Automatically returns original style for the asset code if specific combination not found."
)
async def get_asset(
    code: str,
    domain: str,
    hobby: str,
    style: str,
    db=Depends(get_database)
):
    """
    Get asset with specific combination, automatically returns original style if not found.
    
    - **code**: Asset code identifier
    - **domain**: Domain context (e.g., medical, engineering student)  
    - **hobby**: Hobby context (e.g., movies, gaming, cricket)
    - **style**: Transformation style (visual_cue, storytelling, summary)
    
    Returns the matching asset or automatically returns the original style record for the given asset code.
    """
    try:
        from bson import ObjectId
        
        logger.info(f"Searching for asset: code={code}, domain={domain}, hobby={hobby}, style={style}")
        
        # Try to convert code to ObjectId for search
        search_conditions = []
        
        # Add both ObjectId and string versions of the code to search
        try:
            code_as_objectid = ObjectId(code)
            search_conditions.extend([
                {"code": code_as_objectid},
                {"code": code}
            ])
        except Exception:
            # If not a valid ObjectId, search as string only
            search_conditions.append({"code": code})
        
        # First, try to find exact match with domain, hobby, and style
        for search_condition in search_conditions:
            exact_match = await db["assets"].find_one({
                **search_condition,
                "domain": domain,
                "hobby": hobby,
                "style": style
            })
            
            if exact_match:
                logger.info(f"Found exact match for code={code}, style={style}")
                # Convert ObjectId fields to strings for JSON response
                exact_match["id"] = str(exact_match["_id"])
                del exact_match["_id"]
                if "code" in exact_match and hasattr(exact_match["code"], 'generation_time'):
                    exact_match["code"] = str(exact_match["code"])
                if "created_at" in exact_match and hasattr(exact_match["created_at"], 'isoformat'):
                    exact_match["created_at"] = exact_match["created_at"].isoformat()
                
                return {
                    "found": True,
                    "match_type": "exact",
                    "asset": exact_match
                }
        
        # If no exact match found, always try to find original style record for the given asset code
        logger.info(f"No exact match found, searching for original style: code={code}, style=original")
        
        for search_condition in search_conditions:
            fallback_match = await db["assets"].find_one({
                **search_condition,
                "style": "original"
            })
            
            if fallback_match:
                logger.info(f"Found original style record for code={code}")
                
                # If the requested style is 'original', return the original content
                if style == "original":
                    # Convert ObjectId fields to strings for JSON response
                    fallback_match["id"] = str(fallback_match["_id"])
                    del fallback_match["_id"]
                    if "code" in fallback_match and hasattr(fallback_match["code"], 'generation_time'):
                        fallback_match["code"] = str(fallback_match["code"])
                    if "created_at" in fallback_match and hasattr(fallback_match["created_at"], 'isoformat'):
                        fallback_match["created_at"] = fallback_match["created_at"].isoformat()
                    
                    return {
                        "found": True,
                        "match_type": "default_original",
                        "asset": fallback_match,
                        "note": f"Original style found for asset code '{code}'."
                    }
                
                # If we have original content but need a different style, generate new content
                try:
                    logger.info(f"Generating new {style} content for code={code} using original content")
                    
                    # Use original content to generate new style
                    original_content = fallback_match.get("content", "")
                    
                    if not original_content:
                        raise ValueError("Original content is empty")
                    
                    # Generate new content using AI
                    if style == "original":
                        output = original_content
                    else:
                        # Style-specific prompts
                        style_prompts = {
                            "storytelling": """
### Storytelling Mode:
- Convert the given content into a short storytelling analogy.
- Make it relevant to the given domain and hobby.
- Use simple, engaging language.
- Create a narrative that helps explain the concept.
""",
                            "visual_cue": """
### Visual Cue Mode - Visual Instructions:
- Create text-based visual cues that explain the content.
- Use emojis, arrows (➡️), and symbolic representations.
- Provide 3-4 different visual cue formats.
- Make it hobby and domain relevant.
- Focus on visual learning through text symbols.
""",
                            "summary": """
### Summary Mode:
- Generate a concise summary of the content.
- Make it clear, informative, and easy to understand.
- Use analogies from the hobby to explain domain concepts.
"""
                        }
                        
                        # Create domain-specific context
                        domain_contexts = {
                            "engineering-student": "Use examples in circuits, code snippets, algorithms, and technical implementations",
                            "medical-student": "Use case studies in healthcare, patient scenarios, medical procedures, and clinical examples", 
                            "business-student": "Use marketing examples, finance scenarios, business strategies, and corporate case studies",
                            "teacher-trainer": "Use classroom storytelling, pedagogy techniques, educational methods, and teaching scenarios",
                            "working-professional": "Use real-world workplace analogies, professional scenarios, industry examples, and practical applications"
                        }
                        
                        domain_context = domain_contexts.get(domain, f"Use examples relevant to {domain}")
                        
                        # Create the AI prompt
                        prompt = f"""You are an AI content transformer. 
You will receive inputs for content transformation based on specific learner profiles.

Domain Context: {domain_context}
Hobby Context: Connect concepts to {hobby} for better relatability

Your task is to generate content in the specified style:

{style_prompts[style]}

Now transform this content for {domain} who loves {hobby}:

**Style:** {style}
**Content:** "{original_content}"
**Domain:** {domain} - {domain_context}
**Hobby:** {hobby}

Please provide ONLY the {style} output without any formatting or labels:"""

                        # Generate response using Google Generative AI
                        response = model.generate_content(prompt)
                        
                        if not response.text:
                            raise ValueError("AI failed to generate content")
                        
                        output = response.text.strip()
                        
                        # Clean up any unwanted formatting
                        if output.startswith('"') and output.endswith('"'):
                            output = output[1:-1]
                    
                    # Insert the new generated content into assets collection
                    try:
                        code_as_objectid = ObjectId(code)
                    except Exception:
                        code_as_objectid = code
                        
                    new_asset_data = {
                        "code": code_as_objectid,
                        "content": output,
                        "style": style,
                        "domain": domain,
                        "hobby": hobby,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "status": "not-started"
                    }
                    
                    result = await db["assets"].insert_one(new_asset_data)
                    new_asset_data["id"] = str(result.inserted_id)
                    new_asset_data["code"] = str(new_asset_data["code"])
                    if "created_at" in new_asset_data and hasattr(new_asset_data["created_at"], 'isoformat'):
                        new_asset_data["created_at"] = new_asset_data["created_at"].isoformat()
                    if "updated_at" in new_asset_data and hasattr(new_asset_data["updated_at"], 'isoformat'):
                        new_asset_data["updated_at"] = new_asset_data["updated_at"].isoformat()
                    
                    logger.info(f"Successfully generated and inserted new {style} content for code={code}")
                    
                    return {
                        "found": True,
                        "match_type": "generated",
                        "asset": new_asset_data,
                        "note": f"Generated new {style} content for asset code '{code}' using original content and inserted into database."
                    }
                    
                except Exception as gen_error:
                    logger.error(f"Failed to generate content: {str(gen_error)}")
                    # If generation fails, return original as fallback
                    fallback_match["id"] = str(fallback_match["_id"])
                    del fallback_match["_id"]
                    if "code" in fallback_match and hasattr(fallback_match["code"], 'generation_time'):
                        fallback_match["code"] = str(fallback_match["code"])
                    if "created_at" in fallback_match and hasattr(fallback_match["created_at"], 'isoformat'):
                        fallback_match["created_at"] = fallback_match["created_at"].isoformat()
                    
                    return {
                        "found": True,
                        "match_type": "fallback_original",
                        "asset": fallback_match,
                        "note": f"Content generation failed, returning original style for asset code '{code}'. Error: {str(gen_error)}"
                    }
        
        # No match found at all (neither specific combination nor original style)
        logger.info(f"No asset found for code={code} (neither specific combination nor original style)")
        return {
            "found": False,
            "match_type": "none",
            "asset": None,
            "message": f"No asset found with code='{code}'. Neither the specific combination (domain='{domain}', hobby='{hobby}', style='{style}') nor the default original style exists."
        }
        
    except Exception as e:
        logger.error(f"Error in get_asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset: {str(e)}"
        )

@router.put(
    "/updateAsset",
    summary="Update User Asset Status",
    description="Update the status of an asset for a specific user in a course."
)
async def update_asset(
    course: str = Query(..., description="Course code identifier"),
    asset: str = Query(..., description="Asset code identifier"),
    user: str = Query(..., description="User ID"),
    asset_status: str = Query(..., alias="status", description="Asset status ('not-started', 'in-progress', 'completed')"),
    progress: Optional[int] = Query(None, ge=0, le=100, description="Progress percentage (0-100)"),
    db=Depends(get_database)
):
    """
    Update user asset status in the userassetstatus collection.
    
    - **course**: Course code identifier
    - **asset**: Asset code identifier  
    - **user**: User ID
    - **status**: New status for the asset ('not-started', 'in-progress', 'completed')
    - **progress**: Optional progress percentage (0-100)
    
    Updates or creates a record in the userassetstatus collection for the specific user, course, and asset combination.
    """
    try:
        from bson import ObjectId
        from datetime import datetime
        from app.schemas.user_asset_status import AssetStatus

        # Validate status values
        try:
            status_enum = AssetStatus(asset_status)
        except ValueError:
            valid_statuses = [s.value for s in AssetStatus]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{asset_status}'. Valid statuses are: {', '.join(valid_statuses)}"
            )

        logger.info(f"Updating user asset status: course={course}, asset={asset}, user={user}, status={asset_status}")

        # Create the search condition
        search_condition = {
            "course": course,
            "asset": asset,
            "user": user
        }

        # Prepare update data
        update_data = {
            "status": asset_status,
            "updated_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow()
        }

        # Add progress if provided
        if progress is not None:
            update_data["progress"] = progress

        # Try to update existing record first
        update_result = await db["userassetstatus"].update_one(
            search_condition,
            {"$set": update_data}
        )

        if update_result.matched_count > 0:
            # Record was updated
            logger.info(f"Updated existing user asset status record")
            
            # Get the updated record
            updated_record = await db["userassetstatus"].find_one(search_condition)
            
            if updated_record:
                # Convert ObjectId to string for JSON response
                updated_record["id"] = str(updated_record["_id"])
                del updated_record["_id"]
                
                # Convert any other ObjectId fields to strings
                for key, value in list(updated_record.items()):
                    if hasattr(value, 'generation_time'):  # Check if it's an ObjectId
                        updated_record[key] = str(value)
                
                # Convert datetime fields to ISO format
                for field in ["created_at", "updated_at", "last_accessed"]:
                    if field in updated_record and hasattr(updated_record[field], 'isoformat'):
                        updated_record[field] = updated_record[field].isoformat()

                return {
                    "success": True,
                    "action": "updated",
                    "message": f"Successfully updated user asset status",
                    "course": course,
                    "asset": asset,
                    "user": user,
                    "newStatus": asset_status,
                    "progress": progress,
                    "record": updated_record,
                    "timestamp": datetime.utcnow().isoformat()
                }
        else:
            # No existing record found, create a new one
            logger.info(f"Creating new user asset status record")
            
            new_record_data = {
                **search_condition,
                **update_data,
                "created_at": datetime.utcnow(),
                "progress": progress if progress is not None else 0
            }

            insert_result = await db["userassetstatus"].insert_one(new_record_data)
            
            if insert_result.inserted_id:
                new_record_data["id"] = str(insert_result.inserted_id)
                
                # Convert any ObjectId fields to strings
                for key, value in list(new_record_data.items()):
                    if hasattr(value, 'generation_time'):  # Check if it's an ObjectId
                        new_record_data[key] = str(value)
                
                # Convert datetime fields to ISO format
                for field in ["created_at", "updated_at", "last_accessed"]:
                    if field in new_record_data and hasattr(new_record_data[field], 'isoformat'):
                        new_record_data[field] = new_record_data[field].isoformat()

                return {
                    "success": True,
                    "action": "created",
                    "message": f"Successfully created new user asset status record",
                    "course": course,
                    "asset": asset,
                    "user": user,
                    "newStatus": asset_status,
                    "progress": progress,
                    "record": new_record_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user asset status record"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user asset status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user asset status: {str(e)}"
        )

@router.get(
    "/health",
    summary="Content Transformer Health Check",
    description="Health check endpoint for the content transformer service."
)
async def health_check():
    """Health check for content transformer service"""
    try:
        api_status = "configured" if settings.google_api_key else "not configured"
        model_status = "available" if model else "unavailable"
        
        return {
            "status": "healthy",
            "service": "content_transformer",
            "google_api": api_status,
            "model": model_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )
