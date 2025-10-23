from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import traceback
from app.config.rate_limits import RateLimitConfig
from app.config.rate_limits import limiter
from app.agents.specialized_agents.image_agent import analyze_multiple_images
from app.database.db import get_db
from sqlalchemy.orm import Session
from app.database.repositories.media_repository import MediaRepository
from app.database.repositories.patient_profile_repository import PatientProfileRepository
from app.services.report_generation_service import report_service
from datetime import datetime
import uuid
import base64

router = APIRouter(prefix="/api/image-analysis", tags=["Image Analysis"])

class ImageAnalysisRequest(BaseModel):
    image_urls: List[str]
    patient_id: Optional[str] = None
    analysis_type: str = "comprehensive"  # comprehensive, quick, detailed
    include_pdf: bool = False

class ImageAnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    report_id: Optional[str] = None

@router.post("/analyze", response_model=ImageAnalysisResponse)
@limiter.limit(RateLimitConfig.CHAT)
async def analyze_patient_images(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze multiple patient images and generate a comprehensive hair transplant report.
    
    Args:
        image_urls: List of image URLs from bucket storage
        patient_id: Optional patient ID to associate with the analysis
        analysis_type: Type of analysis (comprehensive, quick, detailed)
        include_pdf: Whether to generate PDF report
        
    Returns:
        Comprehensive hair transplant analysis report
    """
    try:
        # Validate input
        if not analysis_request.image_urls:
            raise HTTPException(
                status_code=400,
                detail="At least one image URL is required"
            )
        
        if len(analysis_request.image_urls) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 images allowed per analysis"
            )
        
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        print(f"🔍 Starting image analysis for {len(analysis_request.image_urls)} images")
        print(f"📊 Report ID: {report_id}")
        
        # Analyze images using enhanced image agent
        analysis_result = await analyze_multiple_images(analysis_request.image_urls)
        
        if "error" in analysis_result:
            raise HTTPException(
                status_code=500,
                detail=f"Image analysis failed: {analysis_result['error']}"
            )
        
        # Enhance the report with additional metadata
        enhanced_report = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "patient_id": analysis_request.patient_id,
            "analysis_type": analysis_request.analysis_type,
            "images_analyzed": len(analysis_request.image_urls),
            "image_urls": analysis_request.image_urls,
            "analysis": analysis_result,
            "status": "completed"
        }
        
        # If patient_id is provided, store the analysis in database
        if analysis_request.patient_id:
            try:
                # Store analysis in patient profile (you might want to create a separate table for this)
                patient_repo = PatientProfileRepository(db)
                patient = patient_repo.get_by_id(analysis_request.patient_id)
                
                if patient:
                    # Update patient with hair transplant analysis
                    # This would require adding a hair_transplant_analysis field to the patient model
                    print(f"📝 Storing analysis for patient {analysis_request.patient_id}")
                else:
                    print(f"⚠️ Patient {analysis_request.patient_id} not found")
                    
            except Exception as e:
                print(f"⚠️ Failed to store analysis in database: {str(e)}")
                # Don't fail the request if database storage fails
        
        # Generate PDF if requested
        if analysis_request.include_pdf:
            try:
                patient_name = "Patient"
                if analysis_request.patient_id:
                    patient_repo = PatientProfileRepository(db)
                    patient = patient_repo.get_by_id(analysis_request.patient_id)
                    if patient:
                        patient_name = patient.name
                
                pdf_content = report_service.generate_pdf_report(enhanced_report, patient_name)
                enhanced_report['pdf_content'] = base64.b64encode(pdf_content).decode('utf-8')
                print(f"📄 PDF report generated successfully")
            except Exception as e:
                print(f"⚠️ Failed to generate PDF: {str(e)}")
                # Don't fail the request if PDF generation fails
        
        print(f"✅ Image analysis completed successfully")
        
        return ImageAnalysisResponse(
            success=True,
            data=enhanced_report,
            report_id=report_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Image analysis error: {str(e)}")
        print(f"❌ Error details: {traceback.format_exc()}")
        
        return ImageAnalysisResponse(
            success=False,
            error=f"Internal server error: {str(e)}"
        )

@router.get("/report/{report_id}")
@limiter.limit(RateLimitConfig.CHAT)
async def get_analysis_report(
    request: Request,
    report_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a previously generated analysis report by report ID.
    
    Args:
        report_id: Unique identifier for the analysis report
        
    Returns:
        The analysis report data
    """
    try:
        # In a real implementation, you would store and retrieve reports from database
        # For now, return a placeholder response
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Report not found. Reports are not currently persisted in database."
            }
        )
        
    except Exception as e:
        print(f"❌ Error retrieving report {report_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve report: {str(e)}"
            }
        )

@router.post("/analyze/quick")
@limiter.limit(RateLimitConfig.CHAT)
async def quick_image_analysis(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Quick image analysis for rapid assessment.
    
    Args:
        image_urls: List of image URLs from bucket storage
        patient_id: Optional patient ID
        
    Returns:
        Quick hair transplant assessment
    """
    try:
        # Set analysis type to quick
        analysis_request.analysis_type = "quick"
        
        # Use the main analyze endpoint with quick type
        return await analyze_patient_images(request, analysis_request, db)
        
    except Exception as e:
        print(f"❌ Quick analysis error: {str(e)}")
        return ImageAnalysisResponse(
            success=False,
            error=f"Quick analysis failed: {str(e)}"
        )

@router.post("/generate-pdf")
@limiter.limit(RateLimitConfig.CHAT)
async def generate_pdf_report(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a PDF report from image analysis.
    
    Args:
        analysis_request: Image analysis request with PDF generation enabled
        
    Returns:
        PDF file download
    """
    try:
        # Enable PDF generation
        analysis_request.include_pdf = True
        
        # Run the analysis
        result = await analyze_patient_images(request, analysis_request, db)
        
        if not result.success or not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate analysis report"
            )
        
        # Extract PDF content
        pdf_content_b64 = result.data.get('pdf_content')
        if not pdf_content_b64:
            raise HTTPException(
                status_code=500,
                detail="PDF content not generated"
            )
        
        # Decode PDF content
        pdf_content = base64.b64decode(pdf_content_b64)
        
        # Return PDF file
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=hair_transplant_analysis_{result.report_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

@router.post("/generate-html")
@limiter.limit(RateLimitConfig.CHAT)
async def generate_html_report(
    request: Request,
    analysis_request: ImageAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an HTML report from image analysis.
    
    Args:
        analysis_request: Image analysis request
        
    Returns:
        HTML report content
    """
    try:
        # Run the analysis
        result = await analyze_patient_images(request, analysis_request, db)
        
        if not result.success or not result.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate analysis report"
            )
        
        # Get patient name
        patient_name = "Patient"
        if analysis_request.patient_id:
            patient_repo = PatientProfileRepository(db)
            patient = patient_repo.get_by_id(analysis_request.patient_id)
            if patient:
                patient_name = patient.name
        
        # Generate HTML report
        html_content = report_service.generate_html_report(result.data, patient_name)
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"inline; filename=hair_transplant_analysis_{result.report_id}.html"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ HTML generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"HTML generation failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for image analysis service.
    """
    return {
        "status": "healthy",
        "service": "image-analysis",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
