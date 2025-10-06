from typing import Dict, List, Any
import config_new as config

class ScreeningLogic:
    def __init__(self):
        self.questions = config.SCREENING_QUESTIONS
    
    def get_next_question(self, current_question: str) -> str:
        """Get the next question in the screening flow"""
        # NEW ORDER: gender -> age_group -> show_types -> city
        question_order = ['gender', 'age_group', 'show_types', 'city']
        
        try:
            current_index = question_order.index(current_question)
            if current_index < len(question_order) - 1:
                return question_order[current_index + 1]
            return None  # Screening complete
        except ValueError:
            return 'gender'  # Start from beginning if invalid
    
    def determine_roles_and_channels(self, screening_data: Dict) -> Dict[str, List[str]]:
        """
        Determine which roles and channels to create/assign based on screening data
        Returns: {'roles': [...], 'channels': [...]}
        
        Hierarchy: gender -> age -> content -> tier
        Example: female -> female-18_24 -> female-18_24-scripted -> female-18_24-scripted-tier1
        """
        roles = []
        channels = []
        
        gender = screening_data.get('gender', [''])[0] if isinstance(screening_data.get('gender'), list) else screening_data.get('gender', '')
        age = screening_data.get('age_group', [''])[0] if isinstance(screening_data.get('age_group'), list) else screening_data.get('age_group', '')
        show_types = screening_data.get('show_types', [])
        city_data = screening_data.get('city', [''])[0] if isinstance(screening_data.get('city'), list) else screening_data.get('city', '')
        
        # Get city tier
        city_info = next((opt for opt in self.questions['city']['options'] 
                        if opt['value'] == city_data), None)
        
        if not city_info:
            tier = 'tier3'
        else:
            tier = city_info.get('tier', 'tier3')
        
        # Create hierarchical structure for each content type selected
        for content_type in show_types:
            # Full role path: gender-age-content-tier
            role_name = config.generate_role_name(gender, age, content_type, tier)
            channel_name = config.generate_channel_name(gender, age, content_type, tier)
            
            roles.append(role_name)
            channels.append(channel_name)
        
        return {
            'roles': roles,
            'channels': channels
        }
    
    def get_user_segments(self, screening_data: Dict) -> Dict[str, Any]:
        """Get user segmentation data"""
        gender = screening_data.get('gender', [''])[0] if isinstance(screening_data.get('gender'), list) else screening_data.get('gender', '')
        age = screening_data.get('age_group', [''])[0] if isinstance(screening_data.get('age_group'), list) else screening_data.get('age_group', '')
        show_types = screening_data.get('show_types', [])
        city_data = screening_data.get('city', [''])[0] if isinstance(screening_data.get('city'), list) else screening_data.get('city', '')
        
        # Get city tier
        city_info = next((opt for opt in self.questions['city']['options'] 
                        if opt['value'] == city_data), None)
        
        tier = city_info.get('tier', 'tier3') if city_info else 'tier3'
        
        segments = {
            'gender': gender,
            'age_group': age,
            'content_types': show_types,
            'city': city_data,
            'tier': tier
        }
        
        return segments
    
    def validate_screening_data(self, screening_data: Dict) -> bool:
        """Validate that all required questions are answered"""
        required_questions = ['gender', 'age_group', 'show_types', 'city']
        
        for question in required_questions:
            if question not in screening_data or not screening_data[question]:
                return False
        
        return True
    
    def get_screening_summary(self, screening_data: Dict) -> str:
        """Generate a summary of the user's screening responses"""
        summary_parts = []
        
        # Gender
        gender = screening_data.get('gender')
        if gender:
            if isinstance(gender, list):
                gender = gender[0]
            gender_info = next((opt for opt in self.questions['gender']['options'] 
                              if opt['value'] == gender), None)
            if gender_info:
                summary_parts.append(f"**Gender:** {gender_info['label']}")
        
        # Age group
        age_group = screening_data.get('age_group')
        if age_group:
            if isinstance(age_group, list):
                age_group = age_group[0]
            age_info = next((opt for opt in self.questions['age_group']['options'] 
                           if opt['value'] == age_group), None)
            if age_info:
                summary_parts.append(f"**Age Group:** {age_info['label']}")
        
        # Show types
        show_types = screening_data.get('show_types', [])
        if show_types:
            type_labels = []
            for show_type in show_types:
                type_info = next((opt for opt in self.questions['show_types']['options'] 
                                if opt['value'] == show_type), None)
                if type_info:
                    type_labels.append(type_info['label'])
            summary_parts.append(f"**Content Types:** {', '.join(type_labels)}")
        
        # City
        city_data = screening_data.get('city')
        if city_data:
            if isinstance(city_data, list):
                city_data = city_data[0]
            city_info = next((opt for opt in self.questions['city']['options'] 
                            if opt['value'] == city_data), None)
            if city_info:
                tier_label = city_info.get('tier', 'tier3').upper().replace('_', ' ')
                summary_parts.append(f"**City:** {city_info['label']} ({tier_label})")
        
        return '\n'.join(summary_parts)
