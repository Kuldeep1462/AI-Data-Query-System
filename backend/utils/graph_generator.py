"""
Graph Generation Utilities
Creates charts and visualizations for query responses
"""

import logging
from typing import Dict, List, Any
import base64
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns

logger = logging.getLogger(__name__)

class GraphGenerator:
    """
    Utility class for generating various types of charts and graphs
    """
    
    def __init__(self):
        # Set style for better looking charts
        plt.style.use('seaborn')
        sns.set_palette("husl")
        logger.info("✅ GraphGenerator initialized")
    
    def create_bar_chart(self, data: Dict[str, Any], title: str = "Bar Chart") -> str:
        """
        Create a bar chart and return as base64 encoded string
        
        Args:
            data: Dictionary with 'labels' and 'values' keys
            title: Chart title
            
        Returns:
            Base64 encoded PNG image string
        """
        try:
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            if not labels or not values:
                return None
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(labels, values, color=sns.color_palette("husl", len(labels)))
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel('Categories', fontsize=12)
            plt.ylabel('Values', fontsize=12)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                        f'₹{value:,.0f}' if value > 1000 else f'{value}',
                        ha='center', va='bottom', fontsize=10)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"❌ Error creating bar chart: {str(e)}")
            return None
    
    def create_pie_chart(self, data: Dict[str, Any], title: str = "Pie Chart") -> str:
        """
        Create a pie chart and return as base64 encoded string
        """
        try:
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            if not labels or not values:
                return None
            
            plt.figure(figsize=(10, 8))
            colors = sns.color_palette("husl", len(labels))
            
            wedges, texts, autotexts = plt.pie(values, labels=labels, colors=colors, 
                                              autopct='%1.1f%%', startangle=90)
            
            plt.title(title, fontsize=16, fontweight='bold')
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"❌ Error creating pie chart: {str(e)}")
            return None
    
    def create_line_chart(self, data: Dict[str, Any], title: str = "Line Chart") -> str:
        """
        Create a line chart and return as base64 encoded string
        """
        try:
            x_values = data.get('x_values', [])
            y_values = data.get('y_values', [])
            
            if not x_values or not y_values:
                return None
            
            plt.figure(figsize=(12, 6))
            plt.plot(x_values, y_values, marker='o', linewidth=2, markersize=8)
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel('Time Period', fontsize=12)
            plt.ylabel('Value', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"❌ Error creating line chart: {str(e)}")
            return None
