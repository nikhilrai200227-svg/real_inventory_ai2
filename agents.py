"""
Multi-Agent Workflow using LangGraph
Specialized agents collaborate to provide comprehensive inventory insights
"""
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime
import json
import pandas as pd

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

class InventoryState(TypedDict):
    """State passed between agents"""
    user_question: str
    forecast_data: dict
    explanation: dict
    recommendations: str
    executive_report: str
    messages: Annotated[list, operator.add]

class InventoryAgents:
    """Multi-agent system for inventory analysis"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize Gemini model if available"""
        try:
            if ChatGoogleGenerativeAI and self.api_key:
                self.model = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.api_key,
                    temperature=0.7
                )
                print("✓ Gemini API initialized")
            else:
                print("⚠ Gemini API not available - using mock responses")
        except Exception as e:
            print(f"⚠ Could not initialize Gemini: {e}")
    
    def forecast_agent(self, state: InventoryState) -> InventoryState:
        """Agent: Analyzes forecast data"""
        try:
            if self.model:
                prompt = f"""
                Analyze this demand forecast data and provide key insights:
                {json.dumps(state['forecast_data'], indent=2)}
                
                Focus on:
                1. Overall trend direction
                2. Peak and low demand periods
                3. Growth rate
                
                Keep response concise and actionable.
                """
                
                response = self.model.invoke(prompt)
                forecast_insight = response.content
            else:
                forecast_insight = self._mock_forecast_insight(state['forecast_data'])
            
            state['messages'].append({
                'agent': 'ForecastAgent',
                'insight': forecast_insight,
                'timestamp': datetime.now().isoformat()
            })
            
            return state
        
        except Exception as e:
            state['messages'].append({
                'agent': 'ForecastAgent',
                'error': str(e)
            })
            return state
    
    def explanation_agent(self, state: InventoryState) -> InventoryState:
        """Agent: Provides explainability for predictions"""
        try:
            if self.model:
                prompt = f"""
                Explain why the demand forecast shows this pattern.
                
                Forecast Details: {json.dumps(state['forecast_data'], indent=2)}
                
                Based on the data, explain:
                1. Key factors driving demand
                2. Seasonal patterns
                3. Anomalies or unusual trends
                
                Use business language, not technical jargon.
                """
                
                response = self.model.invoke(prompt)
                explanation = response.content
            else:
                explanation = self._mock_explanation(state['forecast_data'])
            
            state['explanation'] = explanation
            state['messages'].append({
                'agent': 'ExplanationAgent',
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            })
            
            return state
        
        except Exception as e:
            state['messages'].append({
                'agent': 'ExplanationAgent',
                'error': str(e)
            })
            return state
    
    def recommendation_agent(self, state: InventoryState) -> InventoryState:
        """Agent: Generates actionable recommendations"""
        try:
            if self.model:
                prompt = f"""
                Based on this forecast and explanation, what should the business do?
                
                Question: {state['user_question']}
                Forecast: {json.dumps(state['forecast_data'], indent=2)}
                
                Provide specific, actionable recommendations for:
                1. Inventory levels to maintain
                2. Reorder timing and quantities
                3. Risk mitigation strategies
                4. Opportunity areas
                
                Format as numbered bullet points.
                """
                
                response = self.model.invoke(prompt)
                recommendations = response.content
            else:
                recommendations = self._mock_recommendations(state['forecast_data'])
            
            state['recommendations'] = recommendations
            state['messages'].append({
                'agent': 'RecommendationAgent',
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            })
            
            return state
        
        except Exception as e:
            state['messages'].append({
                'agent': 'RecommendationAgent',
                'error': str(e)
            })
            return state
    
    def executive_agent(self, state: InventoryState) -> InventoryState:
        """Agent: Synthesizes executive summary"""
        try:
            if self.model:
                prompt = f"""
                Create an executive summary of the inventory analysis.
                
                Original Question: {state['user_question']}
                Forecast: {json.dumps(state['forecast_data'], indent=2)}
                Explanation: {state.get('explanation', 'N/A')}
                Recommendations: {state.get('recommendations', 'N/A')}
                
                Format:
                - Executive Summary (2-3 sentences)
                - Key Insights (3-4 bullet points)
                - Recommended Actions (3-4 bullet points)
                - Risk Assessment (1-2 sentences)
                """
                
                response = self.model.invoke(prompt)
                report = response.content
            else:
                report = self._mock_executive_report(state['forecast_data'])
            
            state['executive_report'] = report
            state['messages'].append({
                'agent': 'ExecutiveAgent',
                'report': report,
                'timestamp': datetime.now().isoformat()
            })
            
            return state
        
        except Exception as e:
            state['messages'].append({
                'agent': 'ExecutiveAgent',
                'error': str(e)
            })
            return state
    
    def build_workflow(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(InventoryState)
        
        workflow.add_node("forecast", self.forecast_agent)
        workflow.add_node("explanation", self.explanation_agent)
        workflow.add_node("recommendation", self.recommendation_agent)
        workflow.add_node("executive", self.executive_agent)
        
        workflow.set_entry_point("forecast")
        workflow.add_edge("forecast", "explanation")
        workflow.add_edge("explanation", "recommendation")
        workflow.add_edge("recommendation", "executive")
        workflow.add_edge("executive", END)
        
        return workflow.compile()
    
    def process_query(self, question: str, forecast_data: dict) -> dict:
        """Process user question through agent workflow"""
        
        initial_state = {
            'user_question': question,
            'forecast_data': forecast_data,
            'explanation': '',
            'recommendations': '',
            'executive_report': '',
            'messages': []
        }
        
        try:
            workflow = self.build_workflow()
            result = workflow.invoke(initial_state)
            return result
        except Exception as e:
            print(f"Error in workflow: {e}")
            return {**initial_state, 'error': str(e)}
    
    # Mock methods for when API is not available
    def _mock_forecast_insight(self, forecast_data):
        return """
        Forecast Insight:
        - Overall trend shows upward trajectory over the forecast period
        - Peak demand expected mid-period with 15-20% increase
        - Seasonal pattern detected with weekly cycles
        - Recommend increasing inventory by 20-30% before peak period
        """
    
    def _mock_explanation(self, forecast_data):
        return """
        Explanation:
        The demand pattern is driven by seasonal factors combined with recent growth trends.
        Historical data shows consistent weekly patterns, with higher demand on weekdays.
        The forecast incorporates these patterns to predict future demand more accurately.
        """
    
    def _mock_recommendations(self, forecast_data):
        return """
        Recommendations:
        1. Increase safety stock by 25% before forecasted peak
        2. Schedule reorders 2 weeks in advance to avoid stockouts
        3. Monitor actual vs. predicted sales weekly
        4. Adjust inventory levels based on real-time performance
        5. Prepare supply chain for high-demand period
        """
    
    def _mock_executive_report(self, forecast_data):
        return """
        Executive Summary:
        Demand forecasting indicates a positive growth trajectory over the next 30 days,
        with seasonal peaks expected. Inventory optimization opportunities identified.
        
        Key Insights:
        - 15-20% demand increase expected
        - Strong weekly seasonality detected
        - Safety stock improvements needed
        - Growth opportunity in peak periods
        
        Recommended Actions:
        1. Increase inventory levels by 25% preemptively
        2. Accelerate reorder schedules
        3. Monitor competitive landscape during peak season
        4. Prepare marketing push for peak demand
        
        Risk Assessment:
        Moderate stockout risk if supply chain delays occur.
        Recommend increasing safety margins during forecast period.
        """

if __name__ == "__main__":
    agents = InventoryAgents()
    
    # Mock forecast data
    forecast_data = {
        'product_id': 'PROD_001',
        'forecast_days': 30,
        'avg_daily_demand': 150,
        'peak_demand': 180,
        'trend': 'upward',
        'confidence': 0.92
    }
    
    question = "Which products should we reorder and when?"
    
    result = agents.process_query(question, forecast_data)
    
    print("\n📊 Multi-Agent Analysis Complete")
    print("=" * 60)
    print(f"Executive Report:\n{result.get('executive_report', 'N/A')}")
