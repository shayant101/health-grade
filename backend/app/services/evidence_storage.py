import logging
import uuid
from typing import Dict, Any, Optional, List, Union
import boto3
from botocore.exceptions import ClientError

from ..config import settings

class EvidenceStorageService:
    """
    Service for storing and managing evidence files using Cloudflare R2 storage.
    Provides methods for uploading, retrieving, and managing evidence files.
    """
    
    def __init__(self):
        """
        Initialize Cloudflare R2 client using boto3 with specific configuration.
        """
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name='auto'
        )
        self.bucket_name = settings.R2_BUCKET_NAME
    
    async def upload_evidence(
        self, 
        file_content: Union[bytes, str], 
        file_type: str, 
        scan_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload evidence file to Cloudflare R2 storage.
        
        Args:
            file_content (Union[bytes, str]): File content to upload
            file_type (str): Type of evidence (e.g., 'screenshot', 'report')
            scan_id (str): Associated scan ID
            metadata (Optional[Dict[str, str]]): Additional metadata
        
        Returns:
            Dict[str, Any]: Upload result with file details
        """
        try:
            # Generate unique filename
            file_extension = self._get_file_extension(file_type)
            filename = f"{scan_id}/{file_type}_{uuid.uuid4()}.{file_extension}"
            
            # Convert string to bytes if needed
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            # Upload to R2
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=self._get_mime_type(file_extension),
                Metadata=metadata or {}
            )
            
            # Generate public URL
            public_url = self._generate_public_url(filename)
            
            return {
                "success": True,
                "filename": filename,
                "url": public_url,
                "scan_id": scan_id
            }
        
        except ClientError as e:
            logging.error(f"R2 upload error: {e}")
            return {
                "success": False,
                "error": str(e),
                "scan_id": scan_id
            }
    
    async def list_evidence(
        self, 
        scan_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all evidence files for a specific scan.
        
        Args:
            scan_id (str): Scan ID to list evidence for
        
        Returns:
            List[Dict[str, Any]]: List of evidence file details
        """
        try:
            # List objects with scan_id prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{scan_id}/"
            )
            
            # Process and return evidence details
            return [
                {
                    "filename": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'],
                    "url": self._generate_public_url(obj['Key'])
                }
                for obj in response.get('Contents', [])
            ]
        
        except ClientError as e:
            logging.error(f"R2 list evidence error: {e}")
            return []
    
    async def delete_evidence(
        self, 
        filename: str
    ) -> Dict[str, Any]:
        """
        Delete a specific evidence file.
        
        Args:
            filename (str): Full filename to delete
        
        Returns:
            Dict[str, Any]: Deletion result
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            return {
                "success": True,
                "filename": filename
            }
        
        except ClientError as e:
            logging.error(f"R2 delete evidence error: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _generate_public_url(self, filename: str) -> str:
        """
        Generate a public URL for the stored file.
        
        Args:
            filename (str): Filename to generate URL for
        
        Returns:
            str: Public URL for the file
        """
        return f"https://{self.bucket_name}.r2.cloudflarestorage.com/{filename}"
    
    @staticmethod
    def _get_file_extension(file_type: str) -> str:
        """
        Determine file extension based on file type.
        
        Args:
            file_type (str): Type of evidence
        
        Returns:
            str: Appropriate file extension
        """
        extension_map = {
            'screenshot': 'png',
            'report': 'pdf',
            'log': 'txt',
            'html': 'html',
            'json': 'json'
        }
        
        return extension_map.get(file_type.lower(), 'txt')
    
    @staticmethod
    def _get_mime_type(extension: str) -> str:
        """
        Get MIME type for a given file extension.
        
        Args:
            extension (str): File extension
        
        Returns:
            str: Corresponding MIME type
        """
        mime_types = {
            'png': 'image/png',
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'html': 'text/html',
            'json': 'application/json'
        }
        
        return mime_types.get(extension.lower(), 'application/octet-stream')
    
    async def store_scan_evidence(
        self, 
        scan_id: str, 
        evidence_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Store multiple pieces of evidence for a scan.
        
        Args:
            scan_id (str): Scan ID
            evidence_data (Dict[str, Any]): Evidence to store
        
        Returns:
            List[Dict[str, Any]]: List of uploaded evidence details
        """
        uploaded_evidence = []
        
        # Store website screenshot
        if evidence_data.get('website_screenshot'):
            screenshot_result = await self.upload_evidence(
                file_content=evidence_data['website_screenshot'],
                file_type='screenshot',
                scan_id=scan_id,
                metadata={'source': 'website_analysis'}
            )
            uploaded_evidence.append(screenshot_result)
        
        # Store performance report
        if evidence_data.get('performance_report'):
            report_result = await self.upload_evidence(
                file_content=evidence_data['performance_report'],
                file_type='report',
                scan_id=scan_id,
                metadata={'source': 'pagespeed_insights'}
            )
            uploaded_evidence.append(report_result)
        
        return uploaded_evidence