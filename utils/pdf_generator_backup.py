from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import pandas as pd
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Alphalens brand color
        self.brand_color = colors.HexColor('#FF6B35')
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=26,
            textColor=self.brand_color,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=self.brand_color,
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        self.card_heading_style = ParagraphStyle(
            'CardHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=self.brand_color,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
    
    def create_card_table(self, data, col_widths=None, header_color=None):
        """Create a professional card-style table"""
        if header_color is None:
            header_color = self.brand_color
            
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return table

    def generate_report(self, analysis_results, portfolio_data, recommendations, filename="portfolio_report.pdf"):
        """Generate comprehensive PDF report with all web data"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        # Container for elements
        elements = []
        
        # Add logo
        try:
            logo = Image("attached_assets/Alphalens_1760976199318.png", width=4*inch, height=1.5*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
        except:
            pass  # If logo not found, continue without it
        
        # Title Page
        elements.append(Paragraph("Indian Stock Market", self.title_style))
        elements.append(Paragraph("Portfolio Analysis Report", self.title_style))
        elements.append(Spacer(1, 30))
        
        # Report date
        report_date = datetime.now().strftime('%d %B %Y')
        date_style = ParagraphStyle('Date', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=12)
        elements.append(Paragraph(f"Generated on: {report_date}", date_style))
        elements.append(Spacer(1, 50))
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.heading_style))
        summary = analysis_results['portfolio_summary']
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Investment', f"₹{summary['total_investment']:,.2f}"],
            ['Current Value', f"₹{summary['current_value']:,.2f}"],
            ['Total Gain/Loss', f"₹{summary['total_gain_loss']:+,.2f}"],
            ['Return %', f"{summary['total_gain_loss_percentage']:+.2f}%"],
            ['Number of Stocks', f"{summary['number_of_stocks']}"],
            ['Profitable Stocks', f"{summary['profitable_stocks']}"],
            ['Loss-making Stocks', f"{summary['loss_making_stocks']}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(PageBreak())
        
        # Portfolio Holdings
        elements.append(Paragraph("Portfolio Holdings", self.heading_style))
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        holdings_data = [['Stock', 'Sector', 'Qty', 'Buy Price', 'Current', 'Gain/Loss %']]
        
        for _, stock in stock_performance.iterrows():
            holdings_data.append([
                stock['Stock Name'],
                stock['Sector'],
                f"{stock['Quantity']:.0f}",
                f"₹{stock['Buy Price']:.2f}",
                f"₹{stock['Current Price']:.2f}",
                f"{stock['Percentage Gain/Loss']:+.2f}%"
            ])
        
        holdings_table = Table(holdings_data, colWidths=[1.5*inch, 1.2*inch, 0.7*inch, 1*inch, 1*inch, 1*inch])
        holdings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(holdings_table)
        elements.append(PageBreak())
        
        # Sector Analysis
        elements.append(Paragraph("Sector Analysis", self.heading_style))
        sector_analysis = pd.DataFrame(analysis_results['sector_analysis'])
        
        sector_data = [['Sector', 'Stocks', 'Investment', 'Current Value', 'Return %', '% of Portfolio']]
        
        for _, sector in sector_analysis.iterrows():
            sector_data.append([
                sector['Sector'],
                f"{sector['Number of Stocks']:.0f}",
                f"₹{sector['Investment Value']:,.0f}",
                f"₹{sector['Current Value']:,.0f}",
                f"{sector['Sector Return %']:+.2f}%",
                f"{sector['Percentage of Portfolio']:.1f}%"
            ])
        
        sector_table = Table(sector_data, colWidths=[1.5*inch, 0.7*inch, 1.3*inch, 1.3*inch, 1*inch, 1*inch])
        sector_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(sector_table)
        elements.append(Spacer(1, 30))
        
        # Recommendations Summary
        elements.append(PageBreak())
        elements.append(Paragraph("Investment Recommendations", self.heading_style))
        
        # Count recommendations
        buy_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY')
        hold_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'HOLD')
        sell_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL')
        
        rec_summary = [
            ['Action', 'Count', 'Description'],
            ['BUY', f"{buy_count}", 'Stocks recommended for accumulation'],
            ['HOLD', f"{hold_count}", 'Stocks to maintain position'],
            ['SELL', f"{sell_count}", 'Stocks recommended for exit']
        ]
        
        rec_table = Table(rec_summary, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(rec_table)
        elements.append(Spacer(1, 20))
        
        # Detailed recommendations
        elements.append(Paragraph("Detailed Stock Recommendations", self.subheading_style))
        
        rec_details = [['Stock', 'Action', 'Confidence', 'Rationale']]
        
        for rec in recommendations[:10]:  # Limit to top 10
            action = rec['overall_recommendation']['action']
            confidence = rec['overall_recommendation']['confidence']
            rationale = ' | '.join(rec['overall_recommendation']['rationale'][:2])  # First 2 reasons
            
            rec_details.append([
                rec['stock_name'],
                action,
                confidence,
                rationale[:80] + '...' if len(rationale) > 80 else rationale
            ])
        
        rec_detail_table = Table(rec_details, colWidths=[1.2*inch, 0.8*inch, 1*inch, 3.5*inch])
        rec_detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(rec_detail_table)
        elements.append(PageBreak())
        
        # Disclaimer
        elements.append(Paragraph("Disclaimer", self.heading_style))
        disclaimer_text = """
        This report is generated for informational purposes only and should not be considered as investment advice. 
        Past performance is not indicative of future results. All investments involve risk, including the potential loss of principal. 
        Please consult with a qualified financial advisor before making any investment decisions. The analysis is based on 
        historical data and current market conditions which may change. Individual stock recommendations are based on quantitative 
        analysis and do not account for all market factors or individual circumstances.
        """
        elements.append(Paragraph(disclaimer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return filename
    
    def create_chart_image(self, data, chart_type='bar', title='Chart'):
        """Create a matplotlib chart and return as image buffer"""
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        if chart_type == 'bar':
            ax.bar(data.index, data.values)
        elif chart_type == 'pie':
            ax.pie(data.values, labels=data.index, autopct='%1.1f%%')
        
        ax.set_title(title)
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
