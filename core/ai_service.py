"""
AI Services for TBZ Blogs
Handles all AI-powered features using REST API to avoid SSL issues
Reference: https://ai.google.dev/docs/
"""

import json
import os
from django.conf import settings

# Try to use requests with SSL disabled
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AIService:
    """Main AI Service using REST API for Google Generative AI"""
    
    def __init__(self):
        """Initialize AI service with Gemini REST API"""
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.enabled = settings.AI_ENABLED and self.api_key and REQUESTS_AVAILABLE
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def is_available(self):
        """Check if AI service is available"""
        return self.enabled
    
    def _call_gemini_api(self, prompt: str) -> dict:
        """
        Call Gemini API using REST endpoint
        
        Args:
            prompt: The prompt to send to the model
        
        Returns:
            dict with the API response or error
        """
        if not self.is_available():
            return {'error': 'AI service not available'}
        
        try:
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json",
            }
            
            # Make request with SSL verification disabled
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                json=payload,
                headers=headers,
                timeout=30,
                verify=False  # Disable SSL verification
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    if len(candidate['content']['parts']) > 0:
                        text = candidate['content']['parts'][0].get('text', '')
                        return {'success': True, 'text': text}
            
            return {'error': 'No response from AI model'}
        
        except requests.exceptions.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Failed to parse API response: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def generate_blog_from_idea(self, idea: str, length: str = "medium") -> dict:
        """
        Generate a complete blog post from a raw idea
        
        Args:
            idea: The main idea or topic for the blog
            length: 'short' (500 words), 'medium' (1000 words), 'long' (2000+ words)
        
        Returns:
            dict with 'title', 'content', 'excerpt', 'category'
        """
        if not self.is_available():
            return {'error': 'AI service not available'}
        
        length_guide = {
            'short': '500 words',
            'medium': '1000 words',
            'long': '2000 words'
        }
        
        prompt = f"""Create a blog post about: {idea}

Length: {length_guide.get(length, '1000 words')}

Respond in JSON format:
{{"title": "...", "content": "<h2>...</h2><p>...</p>", "excerpt": "...", "category": "..."}}"""
        
        result = self._call_gemini_api(prompt)
        
        if 'error' in result:
            return result
        
        try:
            text = result['text']
            # Try to extract JSON from the response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(text)
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {'error': f'Failed to parse AI response: {str(e)}'}
    
    def enhance_content(self, content: str, style: str = "professional") -> dict:
        """
        Enhance existing blog content
        
        Args:
            content: The blog content to enhance
            style: 'professional', 'funny', 'casual', 'academic', 'engaging'
        
        Returns:
            dict with 'enhanced_content' and 'improvements'
        """
        if not self.is_available():
            return {'error': 'AI service not available'}
        
        prompt = f"""Enhance this content to be more {style}:

{content}

Respond in JSON format:
{{"enhanced_content": "...", "improvements": ["...", "..."], "readability_score": {{"original_score": 7, "enhanced_score": 9}}}}"""
        
        result = self._call_gemini_api(prompt)
        
        if 'error' in result:
            return result
        
        try:
            text = result['text']
            # Try to extract JSON from the response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(text)
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {'error': f'Failed to parse AI response: {str(e)}'}
    
    def translate_content(self, content: str, target_language: str) -> dict:
        """
        Translate blog content to another language
        
        Args:
            content: The blog content to translate
            target_language: Target language (e.g., 'Spanish', 'French', 'German')
        
        Returns:
            dict with 'translated_content' and 'language'
        """
        if not self.is_available():
            return {'error': 'AI service not available'}
        
        prompt = f"""Translate to {target_language}:

{content}

Respond in JSON format:
{{"translated_content": "...", "language": "{target_language}", "translation_notes": "..."}}"""
        
        result = self._call_gemini_api(prompt)
        
        if 'error' in result:
            return result
        
        try:
            text = result['text']
            # Try to extract JSON from the response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(text)
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {'error': f'Failed to parse AI response: {str(e)}'}
    
    def suggest_images(self, content: str, blog_title: str) -> dict:
        """
        Suggest relevant images for blog content
        
        Args:
            content: The blog content
            blog_title: The blog title
        
        Returns:
            dict with image search queries and suggestions
        """
        if not self.is_available():
            return {'error': 'AI service not available'}
        
        prompt = f"""Suggest images for blog titled '{blog_title}':

{content[:500]}

Respond in JSON format:
{{"search_queries": ["...", "..."], "image_suggestions": ["...", "..."], "unsplash_keywords": ["..."], "pexels_keywords": ["..."]}}"""
        
        result = self._call_gemini_api(prompt)
        
        if 'error' in result:
            return result
        
        try:
            text = result['text']
            # Try to extract JSON from the response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            parsed = json.loads(text)
            return parsed
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            return {'error': f'Failed to parse AI response: {str(e)}'}


# Initialize AI service
ai_service = AIService()
