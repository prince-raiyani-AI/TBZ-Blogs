"""
Sentiment Analysis Service for Comments
Analyzes comment sentiment and provides insights
Reference: https://textblob.readthedocs.io/
"""

from textblob import TextBlob
from enum import Enum


class SentimentType(Enum):
    """Sentiment classification types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalyzer:
    """Analyze sentiment of blog comments"""
    
    def __init__(self):
        """Initialize sentiment analyzer"""
        self.positive_threshold = 0.1
        self.negative_threshold = -0.1
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment of given text
        
        Args:
            text: The comment text to analyze
        
        Returns:
            dict with sentiment type, polarity, and subjectivity
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment type
            if polarity > self.positive_threshold:
                sentiment = SentimentType.POSITIVE.value
            elif polarity < self.negative_threshold:
                sentiment = SentimentType.NEGATIVE.value
            else:
                sentiment = SentimentType.NEUTRAL.value
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 3),  # -1 to 1
                'subjectivity': round(subjectivity, 3),  # 0 to 1
                'confidence': round(abs(polarity), 3)
            }
        except Exception as e:
            return {
                'sentiment': SentimentType.NEUTRAL.value,
                'polarity': 0,
                'subjectivity': 0,
                'error': str(e)
            }
    
    def classify_comment_importance(self, text: str) -> dict:
        """
        Classify comment importance for actionable feedback
        
        Importance levels:
        - HIGH: Contains constructive feedback, improvements, detailed insights
        - MEDIUM: General appreciation, suggestions, or observations with feedback potential
        - LOW: Generic comments, spam-like
        
        Args:
            text: The comment text
        
        Returns:
            dict with importance level and reason
        """
        text_lower = text.lower()
        
        # Keywords for different importance levels
        high_importance_keywords = [
            'improve', 'improvement', 'suggest', 'suggestion', 'feedback',
            'consider', 'could better', 'issue', 'problem', 'bug',
            'feature request', 'enhancement', 'detailed', 'comprehensive',
            'research', 'analysis', 'insight', 'perspective', 'however',
            'moreover', 'furthermore', 'alternatively', 'instead', 'better',
            'should', 'could', 'would be better', 'variety', 'different'
        ]
        
        medium_importance_keywords = [
            'great', 'good', 'nice', 'love', 'like', 'awesome',
            'interesting', 'useful', 'helpful', 'appreciate', 'thanks',
            'way', 'by the way', 'though', 'but', 'yet', 'though'
        ]
        
        low_importance_keywords = [
            'ok', 'fine', 'hmm', 'lol', 'yes', 'no', 'cool',
            '+1', 'agreed', 'same', 'this', 'that', 'it is'
        ]
        
        # Count keyword matches
        high_count = sum(1 for kw in high_importance_keywords if kw in text_lower)
        medium_count = sum(1 for kw in medium_importance_keywords if kw in text_lower)
        low_count = sum(1 for kw in low_importance_keywords if kw in text_lower)
        
        # Determine importance based on:
        # 1. Keyword matches
        # 2. Text length (longer = more detailed)
        # 3. Punctuation (? = question, ! = emphasis)
        # 4. Sentiment (negative can indicate constructive criticism)
        
        word_count = len(text.split())
        has_questions = '?' in text
        has_emphasis = '!' in text
        
        # Check if it's constructive feedback (negative sentiment with suggestions)
        blob = TextBlob(text)
        is_negative = blob.sentiment.polarity < -0.1
        has_construction_words = any(word in text_lower for word in ['could', 'should', 'better', 'improve', 'instead', 'variety'])
        
        # Calculate importance score
        score = (high_count * 3) + (medium_count * 1) + (has_questions * 1) + (has_emphasis * 1)
        
        # Boost score if it's constructive criticism (negative but with suggestions)
        if is_negative and has_construction_words:
            score += 4  # Constructive feedback boost
        
        if high_count >= 1 or (is_negative and has_construction_words and word_count >= 15):
            importance = 'HIGH'
            reason = 'Contains constructive feedback or detailed insights'
        elif (medium_count >= 1 and (has_questions or has_construction_words)) or score >= 3:
            importance = 'MEDIUM'
            reason = 'Contains suggestions or observations for improvement'
        else:
            importance = 'LOW'
            reason = 'Generic or minimal engagement'
        
        return {
            'importance': importance,
            'reason': reason,
            'score': score,
            'word_count': word_count,
            'has_questions': has_questions,
            'has_emphasis': has_emphasis
        }
    
    def get_comment_summary(self, comments: list) -> dict:
        """
        Get summary analysis of multiple comments
        
        Args:
            comments: List of comment texts
        
        Returns:
            dict with sentiment distribution and statistics
        """
        if not comments:
            return {
                'total_comments': 0,
                'sentiment_distribution': {},
                'average_polarity': 0,
                'average_subjectivity': 0,
                'high_importance_count': 0,
                'medium_importance_count': 0,
                'low_importance_count': 0
            }
        
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        importance_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        polarities = []
        subjectivities = []
        
        for comment in comments:
            # Analyze sentiment
            sentiment_result = self.analyze_sentiment(comment)
            sentiments[sentiment_result['sentiment']] += 1
            polarities.append(sentiment_result['polarity'])
            subjectivities.append(sentiment_result['subjectivity'])
            
            # Analyze importance
            importance_result = self.classify_comment_importance(comment)
            importance_counts[importance_result['importance']] += 1
        
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        avg_subjectivity = sum(subjectivities) / len(subjectivities) if subjectivities else 0
        
        return {
            'total_comments': len(comments),
            'sentiment_distribution': sentiments,
            'positive_count': sentiments['positive'],
            'negative_count': sentiments['negative'],
            'neutral_count': sentiments['neutral'],
            'positive_percentage': round((sentiments['positive'] / len(comments)) * 100, 1),
            'negative_percentage': round((sentiments['negative'] / len(comments)) * 100, 1),
            'neutral_percentage': round((sentiments['neutral'] / len(comments)) * 100, 1),
            'sentiment_percentages': {
                k: round((v / len(comments)) * 100, 1) for k, v in sentiments.items()
            },
            'average_polarity': round(avg_polarity, 3),
            'average_subjectivity': round(avg_subjectivity, 3),
            'high_importance_count': importance_counts['HIGH'],
            'medium_importance_count': importance_counts['MEDIUM'],
            'low_importance_count': importance_counts['LOW'],
            'high_importance_percentage': round((importance_counts['HIGH'] / len(comments)) * 100, 1) if comments else 0
        }


# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()


# Module-level functions for convenience
def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of given text"""
    return sentiment_analyzer.analyze_sentiment(text)


def classify_comment_importance(text: str) -> dict:
    """Classify comment importance level"""
    return sentiment_analyzer.classify_comment_importance(text)


def get_comment_summary(comments) -> dict:
    """Get summary analysis of multiple comments"""
    # Handle both QuerySet and list
    comment_texts = [c.content if hasattr(c, 'content') else str(c) for c in comments]
    return sentiment_analyzer.get_comment_summary(comment_texts)
