from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import pandas as pd
from datetime import datetime

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Alphalens brand color
        self.brand_color = colors.HexColor('#FF6B35')
        self.light_bg = colors.HexColor('#FFF5F2')
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.brand_color,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.brand_color,
            spaceAfter=12,
            spaceBefore=18,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=self.brand_color,
            borderPadding=8,
            backColor=self.light_bg,
            leftIndent=8,
            rightIndent=8
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
    
    def create_card_table(self, data, col_widths=None, header_color=None):
        """Create a professional card-style table"""
        if header_color is None:
            header_color = self.brand_color
        
        # Create table with or without column widths
        # Note: reportlab's Table uses 'colWidths' (camelCase), not 'col_widths'
        if col_widths:
            table = Table(data, colWidths=col_widths)
        else:
            table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1.5, header_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        return table

    def generate_report(self, analysis_results, portfolio_data, recommendations, filename="portfolio_report.pdf"):
        """Generate comprehensive PDF report with all web data"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=50
        )
        
        elements = []
        
        # ====================
        # COVER PAGE
        # ====================
        try:
            logo = Image("attached_assets/Alphalens_1760976199318.png", width=4.5*inch, height=1.7*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 25))
        except:
            pass
        
        elements.append(Paragraph("Indian Stock Market", self.title_style))
        elements.append(Paragraph("Portfolio Analysis Report", self.title_style))
        elements.append(Spacer(1, 20))
        
        report_date = datetime.now().strftime('%d %B %Y, %I:%M %p')
        elements.append(Paragraph(f"Generated on: {report_date}", self.subtitle_style))
        elements.append(Spacer(1, 40))
        
        # Company footer on cover page
        footer_style = ParagraphStyle('Footer', parent=self.styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.grey)
        elements.append(Paragraph("Alphalens - A product of Edhaz Financial Services Private Limited", footer_style))
        elements.append(Paragraph("Registered Office: Alpine Eco, Doddenekkundi, K R Puram Hobli, Bangalore 560037", footer_style))
        elements.append(Paragraph("Email: hello@thealphamarket.com | Phone: +91-91089 67788", footer_style))
        
        elements.append(PageBreak())
        
        # ====================
        # EXECUTIVE SUMMARY
        # ====================
        elements.append(Paragraph("📊 Executive Summary", self.heading_style))
        elements.append(Spacer(1, 10))
        
        summary = analysis_results['portfolio_summary']
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Investment', f"₹{summary['total_investment']:,.2f}"],
            ['Current Portfolio Value', f"₹{summary['current_value']:,.2f}"],
            ['Total Gain/Loss', f"₹{summary['total_gain_loss']:+,.2f}"],
            ['Portfolio Return', f"{summary['total_gain_loss_percentage']:+.2f}%"],
            ['Number of Stocks', f"{summary['number_of_stocks']}"],
            ['Profitable Stocks', f"{summary['profitable_stocks']} ({summary['profitable_stocks']/summary['number_of_stocks']*100:.1f}%)"],
            ['Loss-making Stocks', f"{summary['loss_making_stocks']} ({summary['loss_making_stocks']/summary['number_of_stocks']*100:.1f}%)"]
        ]
        
        summary_table = self.create_card_table(summary_data, col_widths=[3.5*inch, 3*inch])
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # ====================
        # DETAILED PORTFOLIO HOLDINGS
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("📋 Detailed Portfolio Holdings", self.heading_style))
        elements.append(Spacer(1, 10))
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
        # Main holdings table
        holdings_data = [['Stock', 'Sector', 'Qty', 'Buy Price', 'Current', 'Investment', 'Current Value', 'Gain/Loss', 'Return %']]
        
        for _, stock in stock_performance.iterrows():
            holdings_data.append([
                stock['Stock Name'],
                stock['Sector'],
                f"{stock['Quantity']:.0f}",
                f"₹{stock['Buy Price']:,.0f}",
                f"₹{stock['Current Price']:,.0f}",
                f"₹{stock['Investment Value']:,.0f}",
                f"₹{stock['Current Value']:,.0f}",
                f"₹{stock['Absolute Gain/Loss']:+,.0f}",
                f"{stock['Percentage Gain/Loss']:+.2f}%"
            ])
        
        holdings_table = self.create_card_table(
            holdings_data, 
            col_widths=[1.1*inch, 0.9*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.8*inch, 0.8*inch]
        )
        elements.append(holdings_table)
        elements.append(Spacer(1, 15))
        
        # Stock Performance Metrics Table
        elements.append(Paragraph("📈 Stock Performance Metrics", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        metrics_data = [['Stock', 'Category', 'Volatility', 'All-Time High', 'Max Drawdown', 'Potential to ATH']]
        
        for _, stock in stock_performance.iterrows():
            # Get metrics with safe defaults
            volatility = stock.get('Volatility (%)', 'N/A')
            ath = stock.get('All-Time High (₹)', 'N/A')
            max_dd = stock.get('Max Drawdown (%)', 'N/A')
            potential = stock.get('Potential to ATH (%)', 'N/A')
            
            metrics_data.append([
                stock['Stock Name'],
                stock.get('Category', 'N/A'),
                f"{volatility:.2f}%" if isinstance(volatility, (int, float)) else str(volatility),
                f"₹{ath:,.2f}" if isinstance(ath, (int, float)) else str(ath),
                f"{max_dd:.2f}%" if isinstance(max_dd, (int, float)) else str(max_dd),
                f"{potential:.2f}%" if isinstance(potential, (int, float)) else str(potential)
            ])
        
        metrics_table = self.create_card_table(
            metrics_data,
            col_widths=[1.5*inch, 1.2*inch, 1.2*inch, 1.3*inch, 1.3*inch, 1.3*inch],
            header_color=colors.HexColor('#3498db')
        )
        elements.append(metrics_table)
        
        # ====================
        # SECTOR ANALYSIS
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("🏭 Sector Analysis", self.heading_style))
        elements.append(Spacer(1, 10))
        
        sector_analysis = pd.DataFrame(analysis_results['sector_analysis'])
        
        sector_data = [['Sector', 'Stocks', 'Investment', 'Current Value', 'Gain/Loss', 'Return %', '% of Portfolio']]
        
        for _, sector in sector_analysis.iterrows():
            sector_data.append([
                sector['Sector'],
                f"{sector['Number of Stocks']:.0f}",
                f"₹{sector['Investment Value']:,.0f}",
                f"₹{sector['Current Value']:,.0f}",
                f"₹{sector['Sector Gain/Loss']:+,.0f}",
                f"{sector['Sector Return %']:+.2f}%",
                f"{sector['Percentage of Portfolio']:.1f}%"
            ])
        
        sector_table = self.create_card_table(
            sector_data,
            col_widths=[1.5*inch, 0.7*inch, 1.2*inch, 1.2*inch, 1.1*inch, 1*inch, 1*inch],
            header_color=colors.HexColor('#9b59b6')
        )
        elements.append(sector_table)
        elements.append(Spacer(1, 20))
        
        # ====================
        # CATEGORY ANALYSIS
        # ====================
        if 'category_analysis' in analysis_results and len(analysis_results['category_analysis']) > 0:
            elements.append(Paragraph("📊 Category Analysis (Large/Mid/Small Cap)", self.subheading_style))
            elements.append(Spacer(1, 8))
            
            category_analysis = pd.DataFrame(analysis_results['category_analysis'])
            
            category_data = [['Category', 'Stocks', 'Investment', 'Current Value', 'Return %', '% of Portfolio']]
            
            for _, cat in category_analysis.iterrows():
                category_data.append([
                    cat['Category'],
                    f"{cat['Number of Stocks']:.0f}",
                    f"₹{cat['Investment Value']:,.0f}",
                    f"₹{cat['Current Value']:,.0f}",
                    f"{cat['Category Return %']:+.2f}%",
                    f"{cat['Percentage of Portfolio']:.1f}%"
                ])
            
            category_table = self.create_card_table(
                category_data,
                col_widths=[1.8*inch, 0.9*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch],
                header_color=colors.HexColor('#27ae60')
            )
            elements.append(category_table)
            elements.append(Spacer(1, 15))
        
        # ====================
        # BENCHMARK COMPARISON
        # ====================
        if 'benchmark_comparison' in analysis_results:
            elements.append(PageBreak())
            elements.append(Paragraph("📊 Benchmark Comparison", self.heading_style))
            elements.append(Spacer(1, 10))
            
            benchmark = analysis_results['benchmark_comparison']
            
            benchmark_data = [
                ['Metric', 'Value'],
                ['Portfolio Return', f"{summary['total_gain_loss_percentage']:+.2f}%"],
            ]
            
            # Add each benchmark
            if 'NIFTY 50' in benchmark:
                benchmark_data.append(['NIFTY 50 Return', f"{benchmark['NIFTY 50']['return']:+.2f}%"])
                benchmark_data.append(['Alpha vs NIFTY 50', f"{benchmark['NIFTY 50']['alpha']:+.2f}%"])
            
            if 'NIFTY MIDCAP 100' in benchmark:
                benchmark_data.append(['NIFTY MIDCAP 100 Return', f"{benchmark['NIFTY MIDCAP 100']['return']:+.2f}%"])
                benchmark_data.append(['Alpha vs NIFTY MIDCAP 100', f"{benchmark['NIFTY MIDCAP 100']['alpha']:+.2f}%"])
            
            benchmark_table = self.create_card_table(
                benchmark_data,
                col_widths=[3.5*inch, 2.5*inch],
                header_color=colors.HexColor('#e67e22')
            )
            elements.append(benchmark_table)
            elements.append(Spacer(1, 15))
        
        # ====================
        # INVESTMENT RECOMMENDATIONS
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("💡 Investment Recommendations", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Summary count
        buy_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY')
        hold_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'HOLD')
        sell_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL')
        
        rec_summary_data = [
            ['Action', 'Count', 'Description'],
            ['BUY', f"{buy_count}", 'Stocks recommended for accumulation'],
            ['HOLD', f"{hold_count}", 'Stocks to maintain current position'],
            ['SELL', f"{sell_count}", 'Stocks recommended for exit/reduction']
        ]
        
        rec_summary_table = self.create_card_table(
            rec_summary_data,
            col_widths=[1.5*inch, 1*inch, 4*inch],
            header_color=colors.HexColor('#f39c12')
        )
        elements.append(rec_summary_table)
        elements.append(Spacer(1, 15))
        
        # Value Perspective Recommendations
        elements.append(Paragraph("📈 Value Investing Perspective", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        value_rec_data = [['Stock', 'Action', 'Confidence', 'Key Rationale']]
        
        for rec in recommendations:
            if 'value_perspective' in rec and rec['value_perspective']:
                value_action = rec['value_perspective'].get('recommendation', 'HOLD')
                value_conf = rec['value_perspective'].get('confidence', 'Medium')
                rationale = rec['value_perspective'].get('rationale', ['No rationale'])
                rationale_text = rationale[0][:60] + '...' if len(rationale) > 0 and len(rationale[0]) > 60 else (rationale[0] if len(rationale) > 0 else 'N/A')
                
                value_rec_data.append([
                    rec['stock_name'],
                    value_action,
                    value_conf,
                    rationale_text
                ])
        
        if len(value_rec_data) > 1:
            value_rec_table = self.create_card_table(
                value_rec_data,
                col_widths=[1.3*inch, 0.9*inch, 1.1*inch, 3.5*inch],
                header_color=colors.HexColor('#2980b9')
            )
            elements.append(value_rec_table)
            elements.append(Spacer(1, 12))
        
        # Growth Perspective Recommendations
        elements.append(Paragraph("🚀 Growth Investing Perspective", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        growth_rec_data = [['Stock', 'Action', 'Confidence', 'Key Rationale']]
        
        for rec in recommendations:
            if 'growth_perspective' in rec and rec['growth_perspective']:
                growth_action = rec['growth_perspective'].get('recommendation', 'HOLD')
                growth_conf = rec['growth_perspective'].get('confidence', 'Medium')
                rationale = rec['growth_perspective'].get('rationale', ['No rationale'])
                rationale_text = rationale[0][:60] + '...' if len(rationale) > 0 and len(rationale[0]) > 60 else (rationale[0] if len(rationale) > 0 else 'N/A')
                
                growth_rec_data.append([
                    rec['stock_name'],
                    growth_action,
                    growth_conf,
                    rationale_text
                ])
        
        if len(growth_rec_data) > 1:
            growth_rec_table = self.create_card_table(
                growth_rec_data,
                col_widths=[1.3*inch, 0.9*inch, 1.1*inch, 3.5*inch],
                header_color=colors.HexColor('#16a085')
            )
            elements.append(growth_rec_table)
        
        # ====================
        # TOP PERFORMERS & WORST PERFORMERS
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("🏆 Performance Highlights", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Top 5 performers
        elements.append(Paragraph("Top 5 Performers", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        top_performers = stock_performance.nlargest(5, 'Percentage Gain/Loss')
        top_data = [['Stock', 'Investment', 'Current Value', 'Gain/Loss', 'Return %']]
        
        for _, stock in top_performers.iterrows():
            top_data.append([
                stock['Stock Name'],
                f"₹{stock['Investment Value']:,.0f}",
                f"₹{stock['Current Value']:,.0f}",
                f"₹{stock['Absolute Gain/Loss']:+,.0f}",
                f"{stock['Percentage Gain/Loss']:+.2f}%"
            ])
        
        top_table = self.create_card_table(
            top_data,
            col_widths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch],
            header_color=colors.HexColor('#27ae60')
        )
        elements.append(top_table)
        elements.append(Spacer(1, 15))
        
        # Worst 5 performers
        elements.append(Paragraph("Worst 5 Performers", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        worst_performers = stock_performance.nsmallest(5, 'Percentage Gain/Loss')
        worst_data = [['Stock', 'Investment', 'Current Value', 'Gain/Loss', 'Return %']]
        
        for _, stock in worst_performers.iterrows():
            worst_data.append([
                stock['Stock Name'],
                f"₹{stock['Investment Value']:,.0f}",
                f"₹{stock['Current Value']:,.0f}",
                f"₹{stock['Absolute Gain/Loss']:+,.0f}",
                f"{stock['Percentage Gain/Loss']:+.2f}%"
            ])
        
        worst_table = self.create_card_table(
            worst_data,
            col_widths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch],
            header_color=colors.HexColor('#e74c3c')
        )
        elements.append(worst_table)
        
        # ====================
        # DISCLAIMER & FOOTER
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("⚠️ Disclaimer", self.heading_style))
        elements.append(Spacer(1, 10))
        
        disclaimer_text = """
        This portfolio analysis report is generated for informational purposes only and should not be construed as financial, 
        investment, tax, or legal advice. The information contained in this report is based on historical data and current market 
        conditions, which are subject to change without notice. Past performance is not indicative of future results.
        <br/><br/>
        All investments involve risk, including the potential loss of principal. The analysis, recommendations, and insights provided 
        in this report are based on quantitative analysis and do not account for all market factors, individual circumstances, or 
        personal financial situations. Individual stock recommendations reflect statistical analysis and market trends but should not 
        be considered as guarantees of future performance.
        <br/><br/>
        Before making any investment decisions, we strongly recommend consulting with a qualified financial advisor who can assess 
        your individual financial situation, risk tolerance, and investment objectives. The value and growth perspectives presented 
        in this report represent different investment strategies and should be evaluated in the context of your overall portfolio 
        strategy and financial goals.
        <br/><br/>
        Market conditions, economic factors, regulatory changes, and company-specific events can significantly impact stock 
        performance. Diversification and regular portfolio review are essential components of sound investment management.
        """
        
        disclaimer_para = Paragraph(disclaimer_text, self.styles['Normal'])
        elements.append(disclaimer_para)
        elements.append(Spacer(1, 30))
        
        # Company footer
        elements.append(Paragraph("About Alphalens", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        company_text = """
        <b>Alphalens</b> is a comprehensive portfolio analysis platform developed by <b>Edhaz Financial Services Private Limited</b>. 
        We provide investors with advanced analytical tools to make informed investment decisions through data-driven insights, 
        dual-perspective recommendations, and comprehensive portfolio tracking.
        <br/><br/>
        <b>Registered Office:</b> Alpine Eco, Doddenekkundi, K R Puram Hobli, Bangalore 560037<br/>
        <b>Email:</b> hello@thealphamarket.com<br/>
        <b>Phone:</b> +91-91089 67788
        """
        
        company_para = Paragraph(company_text, self.styles['Normal'])
        elements.append(company_para)
        
        # Build PDF
        doc.build(elements)
        
        return filename
