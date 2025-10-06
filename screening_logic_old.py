from typing import Dict, List, Any
import config

class ScreeningLogic:
    def __init__(self):
        self.questions = config.SCREENING_QUESTIONS
        self.role_mapping = config.ROLE_MAPPING
    
    def get_next_question(self, current_question: str) -> str:
        """Get the next question in the screening flow"""
        question_order = [
            'show_types', 'city', 'age_group', 'gender', 
            'genres', 'viewing_platform', 'education'
        ]
        
        try:
            current_index = question_order.index(current_question)
            if current_index < len(question_order) - 1:
                return question_order[current_index + 1]
            return None  # Screening complete
        except ValueError:
            return 'show_types'  # Start from beginning if invalid
    
    def determine_roles(self, screening_data: Dict) -> List[str]:
        """Determine which roles to assign based on screening data"""
        roles = []
        
        # Primary content type roles
        show_types = screening_data.get('show_types', [])
        for show_type in show_types:
            if show_type in self.role_mapping:
                roles.append(self.role_mapping[show_type])
        
        # City tier roles
        city_data = screening_data.get('city')
        if city_data:
            city_info = next((opt for opt in self.questions['city']['options'] 
                            if opt['value'] == city_data), None)
            if city_info and 'tier' in city_info:
                tier = city_info['tier']
                if tier in self.role_mapping:
                    roles.append(self.role_mapping[tier])
        
        # Add general screened user role
        roles.append('Screened User')
        
        return list(set(roles))  # Remove duplicates
    
    def get_user_segments(self, screening_data: Dict) -> Dict[str, Any]:
        """Get user segmentation data"""
        segments = {
            'primary_cohort': 'mixed',
            'city_tier': 'unknown',
            'age_group': 'unknown',
            'gender': 'unknown',
            'nccs_proxy': 'unknown',
            'viewing_platform': 'unknown'
        }
        
        # Primary cohort
        show_types = screening_data.get('show_types', [])
        if len(show_types) == 1:
            segments['primary_cohort'] = show_types[0]
        elif len(show_types) > 1:
            segments['primary_cohort'] = 'mixed'
        
        # City tier
        city_data = screening_data.get('city')
        if city_data:
            city_info = next((opt for opt in self.questions['city']['options'] 
                            if opt['value'] == city_data), None)
            if city_info and 'tier' in city_info:
                segments['city_tier'] = city_info['tier']
        
        # Age group
        segments['age_group'] = screening_data.get('age_group', 'unknown')
        
        # Gender
        segments['gender'] = screening_data.get('gender', 'unknown')
        
        # NCCS proxy
        education = screening_data.get('education')
        if education:
            education_info = next((opt for opt in self.questions['education']['options'] 
                                 if opt['value'] == education), None)
            if education_info and 'nccs' in education_info:
                segments['nccs_proxy'] = education_info['nccs']
        
        # Viewing platform
        segments['viewing_platform'] = screening_data.get('viewing_platform', 'unknown')
        
        return segments
    
    def validate_screening_data(self, screening_data: Dict) -> bool:
        """Validate that all required questions are answered"""
        required_questions = ['show_types', 'city', 'age_group', 'gender', 'education']
        
        for question in required_questions:
            if question not in screening_data or not screening_data[question]:
                return False
        
        return True
    
    def get_screening_summary(self, screening_data: Dict) -> str:
        """Generate a summary of the user's screening responses"""
        summary_parts = []
        
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
            city_info = next((opt for opt in self.questions['city']['options'] 
                            if opt['value'] == city_data), None)
            if city_info:
                summary_parts.append(f"**City:** {city_info['label']}")
        
        # Age group
        age_group = screening_data.get('age_group')
        if age_group:
            age_info = next((opt for opt in self.questions['age_group']['options'] 
                           if opt['value'] == age_group), None)
            if age_info:
                summary_parts.append(f"**Age Group:** {age_info['label']}")
        
        # Gender
        gender = screening_data.get('gender')
        if gender:
            gender_info = next((opt for opt in self.questions['gender']['options'] 
                              if opt['value'] == gender), None)
            if gender_info:
                summary_parts.append(f"**Gender:** {gender_info['label']}")
        
        return '\n'.join(summary_parts)

