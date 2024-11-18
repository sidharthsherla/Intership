import streamlit as st
import os
import requests
import kaggle
from serpapi import GoogleSearch

class MarketResearchAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def research_company(self, company_name):
        """
        Conduct comprehensive company and industry research
        """
        params = {
            "engine": "google",
            "q": f"{company_name} company overview industry analysis business model",
            "api_key": self.api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extract key research insights
        organic_results = results.get('organic_results', [])
        
        research_insights = {
            'industry_segment': self._identify_industry_segment(company_name),
            'company_overview': [],
            'key_offerings': [],
            'strategic_focus': []
        }
        
        for result in organic_results[:3]:
            research_insights['company_overview'].append({
                'industry_context': result.get('snippet', 'No description'),
                'source_link': result.get('link', '')
            })
        
        return research_insights

    def _identify_industry_segment(self, company_name):
        """
        Identify industry segment for the company
        """
        industry_mapping = {
            'tech': ['technology', 'software', 'cloud', 'digital'],
            'finance': ['bank', 'financial', 'investment', 'fintech'],
            'healthcare': ['medical', 'health', 'pharmaceutical', 'biotech'],
            'retail': ['store', 'ecommerce', 'shopping', 'marketplace'],
            'manufacturing': ['factory', 'industrial', 'production', 'engineering'],
            'automotive': ['car', 'vehicle', 'automotive', 'transportation']
        }
        
        for segment, keywords in industry_mapping.items():
            if any(keyword in company_name.lower() for keyword in keywords):
                return segment
        
        return 'diverse/unclassified'

class UseCaseGenerationAgent:
    def __init__(self, gemini_api_key):
        self.gemini_api_key = gemini_api_key

    def generate_use_cases(self, company_insights):
        """
        Generate AI/ML use cases using the Gemini API based on industry segment
        """
        industry = company_insights.get('industry_segment', 'diverse/unclassified')
        
        # Define the request payload
        payload = {
            "prompt": f"Generate AI/ML use cases for the {industry} industry.",
            "max_tokens": 150
        }

        headers = {
            'Authorization': f'Bearer {self.gemini_api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post('https://api.gemini.com/v1/generate', json=payload, headers=headers)

        if response.status_code == 200:
            return response.json().get('use_cases', [])
        else:
            st.error("Error generating use cases with Gemini API.")
            return []

class ResourceAssetAgent:
    def __init__(self):
        # Set Kaggle config (update path as needed)
        os.environ['KAGGLE_CONFIG_DIR'] = '/path/to/your/folder'
        try:
            kaggle.api.authenticate()
        except Exception as e:
            st.error(f"Kaggle Authentication Error: {e}")

    def collect_datasets(self, company_name, use_cases):
        """
        Search Kaggle for relevant datasets
        """
        datasets = []
        
        search_keywords = [
            company_name,
            use_cases[0]['title'].split()[0] if use_cases else '',
            use_cases[0]['description'].split()[0] if use_cases else ''
        ]
        
        for keyword in search_keywords:
            try:
                kaggle_datasets = kaggle.api.dataset_list(search=keyword, max_results=3)
                for dataset in kaggle_datasets:
                    datasets.append({
                        'company': dataset.title,
                        'description': dataset.description,
                        'link': dataset.url
                    })
            except Exception as e:
                st.warning(f"Dataset search error for {keyword}: {e}")
        
        return datasets

def main():
    st.title("AI Market Research & Use Case Generation")
    
    # API Key inputs
    serpapi_key = st.text_input("Enter SerpAPI Key:", type="password")
    gemini_api_key = st.text_input("Enter Gemini API Key:", type="password")
    company_name = st.text_input("Enter Company Name:")
    
    if st.button("Generate Market Insights"):
        if not serpapi_key or not gemini_api_key or not company_name:
            st.warning("Please enter all API keys and company name")
            return
        
        # Initialize Agents
        research_agent = MarketResearchAgent(serpapi_key)
        usecase_agent = UseCaseGenerationAgent(gemini_api_key)
        resource_agent = ResourceAssetAgent()
        
        # Research Company
        with st.spinner('Conducting Market Research...'):
            company_insights = research_agent.research_company(company_name)
            
            st.subheader("🏢 Company & Industry Overview")
            st.write(f"**Industry Segment:** {company_insights['industry_segment']}") 
            for insight in company_insights['company_overview']:
                st.write(f"**Industry Context:** {insight['industry_context']}")
                st.write(f"**Source:** {insight['source_link']}")
                st.divider()

        # Generate Use Cases
        with st.spinner('Generating Use Cases...'):
            use_cases = usecase_agent.generate_use_cases(company_insights)
            st.subheader("💡 Generated Use Cases")
            for use_case in use_cases:
                st.write(f"- **Title:** {use_case['title']}")
                st.write(f"  **Description:** {use_case['description']}")

        # Collect Datasets
        with st.spinner('Collecting Relevant Datasets...'):
            datasets = resource_agent.collect_datasets(company_name, use_cases)
            st.subheader("📊 Relevant Datasets from Kaggle")
            for dataset in datasets:
                st.write(f"- **Dataset Title:** {dataset['company']}")
                st.write(f"  **Description:** {dataset['description']}")
                st.markdown(f"[Link to Dataset]({dataset['link']})")

if __name__ == "__main__":
    main()
