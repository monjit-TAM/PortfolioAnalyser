from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import pandas as pd
from datetime import datetime
import io
import tempfile
import os

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

    def generate_report(self, analysis_results, portfolio_data, recommendations, filename="portfolio_report.pdf", historical_data=None, current_data=None, dividend_metrics=None, tax_data=None):
        """Generate comprehensive PDF report with all web data including historical performance, rebalancing, and customer profile"""
        
        # Create PDF document with improved margins
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=55
        )
        
        elements = []
        
        # ====================
        # COVER PAGE
        # ====================
        try:
            logo = Image("attached_assets/alphalens-high-resolution-logo_1770288055113.png", width=4.5*inch, height=1.2*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
        except:
            pass
        
        elements.append(Paragraph("Indian Stock Market", self.title_style))
        elements.append(Paragraph("Portfolio Analysis Report", self.title_style))
        elements.append(Spacer(1, 10))
        
        report_date = datetime.now().strftime('%d %B %Y, %I:%M %p')
        elements.append(Paragraph(f"Generated on: {report_date}", self.subtitle_style))
        elements.append(Spacer(1, 10))
        
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
        elements.append(Spacer(1, 15))
        
        # ====================
        # DIVIDEND YIELD METRICS
        # ====================
        self._create_dividend_section(dividend_metrics, elements)
        
        # ====================
        # TAX IMPLICATIONS
        # ====================
        self._create_tax_section(tax_data, analysis_results, elements)
        
        # ====================
        # PERFORMANCE OVERVIEW with CHARTS
        # ====================
        elements.append(PageBreak())
        self._create_performance_charts(analysis_results, elements)
        
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
            col_widths=[1.0*inch, 0.85*inch, 0.4*inch, 0.7*inch, 0.7*inch, 0.85*inch, 0.85*inch, 0.75*inch, 0.7*inch]
        )
        elements.append(holdings_table)
        
        # ====================
        # SECTOR ANALYSIS with CHARTS
        # ====================
        elements.append(PageBreak())
        self._create_sector_charts(analysis_results, elements)
        
        # Detailed Sector Table
        elements.append(Paragraph("📋 Detailed Sector Breakdown", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        sector_analysis = pd.DataFrame(analysis_results['sector_analysis'])
        
        sector_data = [['Sector', 'Stocks', 'Investment', 'Current Value', 'Gain/Loss', 'Return %', '% of Portfolio']]
        
        for _, sector in sector_analysis.iterrows():
            sector_data.append([
                sector['Sector'],
                f"{sector['Number of Stocks']:.0f}",
                f"₹{sector['Investment Value']:,.0f}",
                f"₹{sector['Current Value']:,.0f}",
                f"₹{sector['Absolute Gain/Loss']:+,.0f}",
                f"{sector['Sector Return %']:+.2f}%",
                f"{sector['Percentage of Portfolio']:.1f}%"
            ])
        
        sector_table = self.create_card_table(
            sector_data,
            col_widths=[1.5*inch, 0.7*inch, 1.2*inch, 1.2*inch, 1.1*inch, 1*inch, 1*inch],
            header_color=colors.HexColor('#9b59b6')
        )
        elements.append(sector_table)
        elements.append(Spacer(1, 10))
        
        # ====================
        # CATEGORY ANALYSIS
        # ====================
        if 'category_analysis' in analysis_results and len(analysis_results['category_analysis']) > 0:
            elements.append(Paragraph("📊 Category Analysis (Large/Mid/Small Cap)", self.subheading_style))
            elements.append(Spacer(1, 10))
            
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
            elements.append(Spacer(1, 10))
        
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
            elements.append(Spacer(1, 10))
        
        # ====================
        # BENCHMARK COMPARISON
        # ====================
        elements.append(PageBreak())
        self._create_benchmark_section(analysis_results, portfolio_data, elements)
        
        # ====================
        # INVESTMENT RECOMMENDATIONS
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("💡 Investment Recommendations", self.heading_style))
        
        # Add Recommendation Distribution Chart
        self._create_recommendation_charts(recommendations, elements)
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
        elements.append(Spacer(1, 10))
        
        # Value Perspective Recommendations
        elements.append(Paragraph("📈 Value Investing Perspective", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        value_rec_data = [['Stock', 'Action', 'Key Rationale']]
        
        for rec in recommendations:
            # Access the correct key: value_analysis
            value_persp = rec.get('value_analysis', {})
            if value_persp:
                value_action = value_persp.get('recommendation', 'HOLD')
                rationale = value_persp.get('rationale', [])
                if isinstance(rationale, list) and len(rationale) > 0:
                    rationale_text = rationale[0][:80] + '...' if len(rationale[0]) > 80 else rationale[0]
                else:
                    rationale_text = 'Analysis based on fundamentals'
                
                value_rec_data.append([
                    rec.get('stock_name', 'N/A'),
                    value_action,
                    rationale_text
                ])
        
        if len(value_rec_data) > 1:
            value_rec_table = self.create_card_table(
                value_rec_data,
                col_widths=[1.5*inch, 1*inch, 4.3*inch],
                header_color=colors.HexColor('#2980b9')
            )
            elements.append(value_rec_table)
            elements.append(Spacer(1, 10))
        
        # Growth Perspective Recommendations
        elements.append(Paragraph("🚀 Growth Investing Perspective", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        growth_rec_data = [['Stock', 'Action', 'Key Rationale']]
        
        for rec in recommendations:
            # Access the correct key: growth_analysis
            growth_persp = rec.get('growth_analysis', {})
            if growth_persp:
                growth_action = growth_persp.get('recommendation', 'HOLD')
                rationale = growth_persp.get('rationale', [])
                if isinstance(rationale, list) and len(rationale) > 0:
                    rationale_text = rationale[0][:80] + '...' if len(rationale[0]) > 80 else rationale[0]
                else:
                    rationale_text = 'Analysis based on growth metrics'
                
                growth_rec_data.append([
                    rec.get('stock_name', 'N/A'),
                    growth_action,
                    rationale_text
                ])
        
        if len(growth_rec_data) > 1:
            growth_rec_table = self.create_card_table(
                growth_rec_data,
                col_widths=[1.5*inch, 1*inch, 4.3*inch],
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
        elements.append(Spacer(1, 10))
        
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
        elements.append(Spacer(1, 10))
        
        # Worst 5 performers
        elements.append(Paragraph("Worst 5 Performers", self.subheading_style))
        elements.append(Spacer(1, 10))
        
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
        # HISTORICAL PERFORMANCE with CHARTS
        # ====================
        if historical_data:
            elements.append(PageBreak())
            self._create_historical_performance_charts(historical_data, portfolio_data, elements)
            
            # Additional textual summary
            elements.append(Paragraph("📋 Performance Summary Table", self.subheading_style))
            elements.append(Spacer(1, 10))
            
            # Calculate historical metrics
            portfolio_history = self._calculate_portfolio_history(portfolio_data, historical_data)
            
            if not portfolio_history.empty:
                initial_value = portfolio_history['Portfolio_Value'].iloc[0]
                current_value = portfolio_history['Portfolio_Value'].iloc[-1]
                total_return = ((current_value - initial_value) / initial_value) * 100
                peak_value = portfolio_history['Portfolio_Value'].max()
                current_drawdown = ((current_value - peak_value) / peak_value) * 100
                daily_returns = portfolio_history['Portfolio_Value'].pct_change().dropna()
                volatility = daily_returns.std() * (252 ** 0.5) * 100
                
                hist_summary_data = [
                    ['Metric', 'Value'],
                    ['Initial Portfolio Value', f"₹{initial_value:,.2f}"],
                    ['Current Portfolio Value', f"₹{current_value:,.2f}"],
                    ['Total Return', f"{total_return:+.2f}%"],
                    ['Peak Portfolio Value', f"₹{peak_value:,.2f}"],
                    ['Current Drawdown', f"{current_drawdown:.2f}%"],
                    ['Annualized Volatility', f"{volatility:.2f}%"]
                ]
                
                hist_table = self.create_card_table(
                    hist_summary_data,
                    col_widths=[3.5*inch, 3*inch],
                    header_color=colors.HexColor('#3498db')
                )
                elements.append(hist_table)
        
        # ====================
        # REBALANCING SUGGESTIONS with CHARTS
        # ====================
        elements.append(PageBreak())
        self._create_enhanced_rebalancing_section(analysis_results, current_data, elements)
        
        # Additional Sector Rebalancing if needed
        elements.append(Paragraph("📊 Sector Rebalancing Analysis", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        # Keep minimal sector rebalancing table
        strategy = 'Balanced'
        target_allocation = {
            'Large Cap': 50,
            'Mid Cap': 30,
            'Small Cap': 20
        }
        
        elements.append(Paragraph(f"📊 Recommended Strategy: {strategy}", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        # Current vs Target Allocation
        current_allocation = self._calculate_current_allocation(analysis_results)
        
        allocation_data = [['Category', 'Current %', 'Target %', 'Difference']]
        
        for category in target_allocation.keys():
            current_pct = current_allocation.get(category, 0)
            target_pct = target_allocation[category]
            diff = target_pct - current_pct
            
            allocation_data.append([
                category,
                f"{current_pct:.1f}%",
                f"{target_pct:.1f}%",
                f"{diff:+.1f}%"
            ])
        
        allocation_table = self.create_card_table(
            allocation_data,
            col_widths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch],
            header_color=colors.HexColor('#9b59b6')
        )
        elements.append(allocation_table)
        elements.append(Spacer(1, 10))
        
        # Rebalancing Actions
        elements.append(Paragraph("💡 Recommended Actions", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        rebalancing_actions = self._generate_rebalancing_actions(
            current_allocation, target_allocation, 
            analysis_results['portfolio_summary']['current_value'],
            analysis_results
        )
        
        if rebalancing_actions:
            actions_data = [['Category', 'Action', 'Amount', 'Description']]
            
            for action in rebalancing_actions[:5]:  # Top 5 actions
                actions_data.append([
                    action['category'],
                    action['action'],
                    f"₹{abs(action['amount']):,.0f}",
                    action['description']
                ])
            
            actions_table = self.create_card_table(
                actions_data,
                col_widths=[1.3*inch, 0.8*inch, 1.2*inch, 3.2*inch],
                header_color=colors.HexColor('#e67e22')
            )
            elements.append(actions_table)
        
        # ====================
        # CUSTOMER PROFILE with CHARTS
        # ====================
        elements.append(PageBreak())
        self._create_enhanced_customer_profile_section(analysis_results, recommendations, elements)
        
        # Additional Portfolio Details
        elements.append(Paragraph("📊 Additional Portfolio Details", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        summary = analysis_results['portfolio_summary']
        portfolio_size = summary['current_value']
        num_stocks = summary['number_of_stocks']
        overall_return = summary['total_gain_loss_percentage']
        
        # Categorize investor
        if portfolio_size >= 10000000:
            size_category = "High Net Worth"
        elif portfolio_size >= 2500000:
            size_category = "Affluent Investor"
        elif portfolio_size >= 500000:
            size_category = "Moderate Investor"
        else:
            size_category = "Emerging Investor"
        
        if num_stocks >= 15:
            experience_level = "Experienced"
        elif num_stocks >= 8:
            experience_level = "Intermediate"
        elif num_stocks >= 4:
            experience_level = "Beginner+"
        else:
            experience_level = "Beginner"
        
        if overall_return > 25:
            perf_category = "Excellent"
        elif overall_return > 10:
            perf_category = "Good"
        elif overall_return > 0:
            perf_category = "Positive"
        elif overall_return > -10:
            perf_category = "Moderate Loss"
        else:
            perf_category = "High Loss"
        
        profile_data = [
            ['Aspect', 'Assessment'],
            ['Portfolio Size', f"₹{portfolio_size:,.2f}"],
            ['Investor Category', size_category],
            ['Number of Stocks', f"{num_stocks}"],
            ['Experience Level', experience_level],
            ['Overall Return', f"{overall_return:+.2f}%"],
            ['Performance Status', perf_category]
        ]
        
        profile_table = self.create_card_table(
            profile_data,
            col_widths=[2.5*inch, 4*inch],
            header_color=colors.HexColor('#1abc9c')
        )
        elements.append(profile_table)
        elements.append(Spacer(1, 10))
        
        # Investment Style Analysis
        elements.append(Paragraph("🎯 Investment Style Analysis", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        # Analyze based on recommendations
        value_oriented = sum(1 for rec in recommendations if rec.get('value_analysis', {}).get('recommendation') == 'BUY')
        growth_oriented = sum(1 for rec in recommendations if rec.get('growth_analysis', {}).get('recommendation') == 'BUY')
        
        if value_oriented > growth_oriented:
            primary_style = "Value Investor"
            style_desc = "Focus on undervalued stocks with strong fundamentals"
        elif growth_oriented > value_oriented:
            primary_style = "Growth Investor"
            style_desc = "Focus on high-growth potential stocks"
        else:
            primary_style = "Balanced Investor"
            style_desc = "Balanced approach between value and growth"
        
        style_data = [
            ['Style Aspect', 'Analysis'],
            ['Primary Style', primary_style],
            ['Style Description', style_desc],
            ['Value-oriented Picks', f"{value_oriented} stocks"],
            ['Growth-oriented Picks', f"{growth_oriented} stocks"]
        ]
        
        style_table = self.create_card_table(
            style_data,
            col_widths=[2.5*inch, 4*inch],
            header_color=colors.HexColor('#34495e')
        )
        elements.append(style_table)
        elements.append(Spacer(1, 10))
        
        # Portfolio Health Score
        elements.append(Paragraph("💯 Portfolio Health Score", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        health_score = self._calculate_health_score(analysis_results, recommendations)
        
        if health_score >= 80:
            health_status = "Excellent"
            health_color_hex = '#27ae60'
        elif health_score >= 60:
            health_status = "Good"
            health_color_hex = '#3498db'
        elif health_score >= 40:
            health_status = "Fair"
            health_color_hex = '#f39c12'
        else:
            health_status = "Needs Improvement"
            health_color_hex = '#e74c3c'
        
        health_data = [
            ['Metric', 'Score/Status'],
            ['Overall Health Score', f"{health_score}/100"],
            ['Health Status', health_status],
            ['Diversification', f"{len(analysis_results['sector_analysis'])} sectors"],
            ['Profitable Holdings', f"{summary['profitable_stocks']}/{num_stocks} stocks"]
        ]
        
        health_table = self.create_card_table(
            health_data,
            col_widths=[2.5*inch, 4*inch],
            header_color=colors.HexColor(health_color_hex)
        )
        elements.append(health_table)
        
        # ====================
        # COMPREHENSIVE DISCLAIMER & FOOTER
        # ====================
        elements.append(PageBreak())
        elements.append(Paragraph("⚠️ Important Disclaimers", self.heading_style))
        elements.append(Spacer(1, 12))
        
        # General Disclaimer
        elements.append(Paragraph("General Disclaimer", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        general_disclaimer = """
        This portfolio analysis report is generated for informational purposes only and should not be construed as financial, 
        investment, tax, or legal advice. The information contained in this report is based on historical data and current market 
        conditions, which are subject to change without notice. <b>Past performance is not indicative of future results.</b>
        <br/><br/>
        All investments involve risk, including the potential loss of principal. The analysis, recommendations, and insights provided 
        in this report are based on quantitative analysis and do not account for all market factors, individual circumstances, or 
        personal financial situations.
        """
        elements.append(Paragraph(general_disclaimer, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Investment Disclaimer
        elements.append(Paragraph("Investment Risk Disclaimer", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        investment_disclaimer = """
        Individual stock recommendations in this report reflect statistical analysis and market trends but should not be considered 
        as guarantees of future performance. Before making any investment decisions, we strongly recommend consulting with a 
        SEBI-registered investment advisor who can assess your individual financial situation, risk tolerance, and investment objectives.
        <br/><br/>
        Market conditions, economic factors, regulatory changes, and company-specific events can significantly impact stock performance. 
        Diversification and regular portfolio review are essential components of sound investment management.
        """
        elements.append(Paragraph(investment_disclaimer, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Tax Disclaimer
        elements.append(Paragraph("Tax Disclaimer", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        tax_disclaimer = """
        Tax calculations presented in this report are estimates based on prevailing tax rates as per Union Budget 2024. Actual tax 
        liability may vary based on individual circumstances, applicable exemptions, and deductions. The LTCG exemption of ₹1.25 lakh 
        applies annually and may change with future budgets.
        <br/><br/>
        <b>We strongly recommend consulting with a qualified Chartered Accountant or Tax Advisor for personalized tax planning advice.</b>
        """
        elements.append(Paragraph(tax_disclaimer, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Data Disclaimer
        elements.append(Paragraph("Data Accuracy Disclaimer", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        data_disclaimer = """
        Stock prices and market data are sourced from third-party providers and may be delayed or subject to errors. While we strive 
        to provide accurate information, we do not guarantee the accuracy, completeness, or timeliness of any data presented. 
        Dividend yields are based on trailing twelve-month data and may not reflect future dividend payments.
        """
        elements.append(Paragraph(data_disclaimer, self.styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Regulatory Compliance
        elements.append(Paragraph("Regulatory Compliance", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        regulatory_text = """
        Alphalens is a portfolio analysis tool and does not provide investment advisory services as defined under SEBI (Investment 
        Advisers) Regulations, 2013. We do not execute trades, manage portfolios, or provide personalized investment recommendations. 
        All investment decisions are the sole responsibility of the user.
        """
        elements.append(Paragraph(regulatory_text, self.styles['Normal']))
        elements.append(Spacer(1, 15))
        
        # Company footer
        elements.append(Paragraph("About Alphalens", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        company_text = """
        <b>Alphalens</b> is a comprehensive portfolio analysis platform developed by <b>Edhaz Financial Services Private Limited</b>. 
        We provide investors with advanced analytical tools to make informed investment decisions through data-driven insights, 
        dual-perspective recommendations, and comprehensive portfolio tracking.
        <br/><br/>
        <b>Registered Office:</b> Alpine Eco, Doddenekkundi, K R Puram Hobli, Bangalore 560037<br/>
        <b>CIN:</b> [Company Identification Number]<br/>
        <b>Email:</b> hello@thealphamarket.com<br/>
        <b>Phone:</b> +91-91089 67788<br/>
        <b>Website:</b> www.alphalens.in
        """
        
        company_para = Paragraph(company_text, self.styles['Normal'])
        elements.append(company_para)
        elements.append(Spacer(1, 15))
        
        # Final note
        report_footer = Paragraph(
            f"<i>Report generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')} IST. "
            "This report is confidential and intended solely for the recipient.</i>",
            ParagraphStyle('ReportFooter', parent=self.styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(report_footer)
        
        # Build PDF
        doc.build(elements)
        
        return filename
    
    def _create_performance_charts(self, analysis_results, elements):
        """Add Performance Overview charts to PDF using matplotlib"""
        import matplotlib
        matplotlib.use('Agg')  # Use non-GUI backend
        import matplotlib.pyplot as plt
        from reportlab.lib.utils import ImageReader
        
        elements.append(Paragraph("📈 Performance Overview", self.heading_style))
        elements.append(Spacer(1, 10))
        
        summary = analysis_results['portfolio_summary']
        
        # Chart 1: Stock Performance Distribution
        profit_stocks = summary.get('profitable_stocks', 0)
        loss_stocks = summary.get('loss_making_stocks', 0)
        
        if profit_stocks + loss_stocks > 0:
            fig, ax = plt.subplots(figsize=(7, 3.5))
            categories = ['Profitable', 'Loss-making']
            values = [profit_stocks, loss_stocks]
            colors = ['#27ae60', '#e74c3c']
            
            bars = ax.bar(categories, values, color=colors, width=0.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            ax.set_title('Stock Performance Distribution', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel('Number of Stocks', fontsize=11)
            ax.set_xlabel('Performance Category', fontsize=11)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            plt.tight_layout()
            
            # Save to BytesIO
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            # Add to PDF
            img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
            elements.append(img)
            elements.append(Spacer(1, 8))
        
        # Chart 2: Investment vs Current Value
        total_investment = summary.get('total_investment', 0)
        current_value = summary.get('current_value', 0)
        
        if total_investment > 0 or current_value > 0:
            fig, ax = plt.subplots(figsize=(7, 3.5))
            categories = ['Investment', 'Current Value']
            values = [total_investment, current_value]
            colors = ['#3498db', '#2c3e50']
            
            bars = ax.bar(categories, values, color=colors, width=0.5)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{height:,.0f}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.set_title('Investment vs Current Portfolio Value', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel('Amount (₹)', fontsize=11)
            ax.ticklabel_format(style='plain', axis='y')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            plt.tight_layout()
            
            # Save to BytesIO
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            # Add to PDF
            img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
            elements.append(img)
            elements.append(Spacer(1, 5))
    
    def _create_sector_charts(self, analysis_results, elements):
        """Add Sector Analysis charts and insights to PDF using matplotlib"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from reportlab.lib.utils import ImageReader
        
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        
        if sector_data.empty:
            return
        
        elements.append(Paragraph("🏭 Sector Analysis", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Sector Allocation Pie Chart
        fig, ax = plt.subplots(figsize=(7, 4))
        colors = plt.cm.Set3(range(len(sector_data)))
        
        wedges, texts, autotexts = ax.pie(
            sector_data['Current Value'],
            labels=sector_data['Sector'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Sector Allocation by Value', fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=3.2*inch)
        elements.append(img)
        elements.append(Spacer(1, 8))
        
        # Sector Performance Bar Chart
        fig, ax = plt.subplots(figsize=(7, 3.5))
        colors_bar = ['#27ae60' if x >= 0 else '#e74c3c' for x in sector_data['Sector Return %']]
        
        bars = ax.bar(sector_data['Sector'], sector_data['Sector Return %'], color=colors_bar, width=0.6)
        
        # Add value labels on bars
        for bar, value in zip(bars, sector_data['Sector Return %']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:+.2f}%',
                   ha='center', va='bottom' if height >= 0 else 'top',
                   fontsize=10, fontweight='bold')
        
        ax.set_title('Sector-wise Returns (%)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Sector', fontsize=11)
        ax.set_ylabel('Return %', fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
        elements.append(img)
        elements.append(Spacer(1, 5))
        
        # Sector Insights
        elements.append(Paragraph("💡 Sector Insights", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        best_sector = sector_data.loc[sector_data['Sector Return %'].idxmax()]
        worst_sector = sector_data.loc[sector_data['Sector Return %'].idxmin()]
        most_allocated = sector_data.loc[sector_data['Current Value'].idxmax()]
        
        insights_data = [
            ['Insight', 'Details'],
            ['Best Performing Sector', f"{best_sector['Sector']} ({best_sector['Sector Return %']:+.2f}%)"],
            ['Worst Performing Sector', f"{worst_sector['Sector']} ({worst_sector['Sector Return %']:+.2f}%)"],
            ['Most Allocated Sector', f"{most_allocated['Sector']} (₹{most_allocated['Current Value']:,.0f}, {most_allocated['Percentage of Portfolio']:.1f}%)"],
            ['Total Sectors', f"{len(sector_data)} sectors"]
        ]
        
        insights_table = self.create_card_table(insights_data, col_widths=[2*inch, 4.5*inch])
        elements.append(insights_table)
        elements.append(Spacer(1, 10))
        
        # Diversification Analysis
        num_sectors = len(sector_data)
        max_sector_pct = sector_data['Percentage of Portfolio'].max()
        
        elements.append(Paragraph("📊 Diversification Analysis", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        div_data = [
            ['Metric', 'Value', 'Assessment'],
            ['Number of Sectors', str(num_sectors), 
             'Excellent' if num_sectors >= 6 else 'Good' if num_sectors >= 4 else 'Needs Improvement'],
            ['Max Sector Concentration', f"{max_sector_pct:.1f}%",
             'Low Risk' if max_sector_pct < 30 else 'Moderate Risk' if max_sector_pct < 50 else 'High Risk']
        ]
        
        div_table = self.create_card_table(div_data, col_widths=[2*inch, 1.5*inch, 2*inch])
        elements.append(div_table)
        elements.append(Spacer(1, 10))
        
        # Sector Recommendations
        elements.append(Paragraph("💡 Sector Recommendations", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        rec_text = []
        if max_sector_pct > 40:
            rec_text.append(f"• Consider reducing exposure to {most_allocated['Sector']} (currently {max_sector_pct:.1f}%)")
        if num_sectors < 5:
            rec_text.append("• Diversify into additional sectors to reduce concentration risk")
        if worst_sector['Sector Return %'] < -15:
            rec_text.append(f"• Review holdings in {worst_sector['Sector']} sector (currently {worst_sector['Sector Return %']:+.2f}%)")
        if best_sector['Sector Return %'] > 20:
            rec_text.append(f"• Consider booking partial profits in {best_sector['Sector']} sector")
        
        if rec_text:
            for rec in rec_text:
                elements.append(Paragraph(rec, self.styles['Normal']))
        else:
            elements.append(Paragraph("• Your sector allocation is well-balanced", self.styles['Normal']))
        
        elements.append(Spacer(1, 10))
    
    def _create_recommendation_charts(self, recommendations, elements):
        """Add Recommendation charts to PDF using matplotlib"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from reportlab.lib.utils import ImageReader
        
        if not recommendations:
            return
        
        # Count recommendations
        buy_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY')
        hold_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'HOLD')
        sell_count = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL')
        
        # Recommendation Distribution Pie Chart
        if buy_count + hold_count + sell_count > 0:
            elements.append(Paragraph("📊 Recommendation Distribution", self.subheading_style))
            elements.append(Spacer(1, 10))
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            values = [buy_count, hold_count, sell_count]
            labels = ['BUY', 'HOLD', 'SELL']
            colors = ['#27ae60', '#f39c12', '#e74c3c']
            
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Recommendation Distribution', fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()
            
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            img = Image(img_bytes, width=5*inch, height=2.6*inch)
            elements.append(img)
            elements.append(Spacer(1, 5))
    
    def _create_benchmark_section(self, analysis_results, portfolio_data, elements):
        """Add comprehensive Benchmark Comparison section to PDF"""
        from utils.data_fetcher import DataFetcher
        
        elements.append(Paragraph("📊 Benchmark Comparison", self.heading_style))
        elements.append(Spacer(1, 10))
        
        stock_performance = pd.DataFrame(analysis_results['stock_performance'])
        
        if stock_performance.empty:
            return
        
        # Portfolio vs Market Indices
        elements.append(Paragraph("🎯 Portfolio vs Market Indices", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        portfolio_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        
        # Get benchmark returns
        data_fetcher = DataFetcher()
        benchmark_mapping = {
            'Large Cap': 'NIFTY50',
            'Mid Cap': 'NIFTY_MIDCAP_100',
            'Small Cap': 'NIFTY_SMALLCAP_100'
        }
        
        # Calculate benchmark returns
        benchmark_returns = {}
        for category, benchmark in benchmark_mapping.items():
            category_stocks = stock_performance[stock_performance['Category'] == category]
            if not category_stocks.empty:
                avg_buy_date = pd.to_datetime(portfolio_data[portfolio_data['Stock Name'].isin(category_stocks['Stock Name'])]['Buy Date']).min()
                if pd.notna(avg_buy_date):
                    bench_data = data_fetcher.get_index_data(benchmark, avg_buy_date.strftime('%Y-%m-%d'))
                    if not bench_data.empty:
                        bench_return = ((bench_data['Close'].iloc[-1] - bench_data['Close'].iloc[0]) / bench_data['Close'].iloc[0]) * 100
                        benchmark_returns[benchmark] = bench_return
        
        # Benchmark comparison table
        bench_data = [
            ['Index', 'Return', 'vs Portfolio'],
            ['Portfolio', f"{portfolio_return:+.2f}%", '-'],
        ]
        
        for index_name, return_val in benchmark_returns.items():
            diff = portfolio_return - return_val
            bench_data.append([index_name, f"{return_val:+.2f}%", f"{diff:+.2f}%"])
        
        bench_table = self.create_card_table(bench_data, col_widths=[2.5*inch, 1.5*inch, 2*inch])
        elements.append(bench_table)
        elements.append(Spacer(1, 10))
        
        # Benchmark Insights
        elements.append(Paragraph("💡 Benchmark Insights", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        insights = []
        nifty_return = benchmark_returns.get('NIFTY50', 0)
        if portfolio_return > nifty_return:
            insights.append(f"• Your portfolio is outperforming NIFTY 50 by {portfolio_return - nifty_return:+.2f}%")
        else:
            insights.append(f"• Your portfolio is underperforming NIFTY 50 by {abs(portfolio_return - nifty_return):.2f}%")
        
        if portfolio_return > 0:
            insights.append("• Your portfolio is generating positive returns")
        else:
            insights.append("• Consider reviewing your investment strategy to improve returns")
        
        for insight in insights:
            elements.append(Paragraph(insight, self.styles['Normal']))
        
        elements.append(Spacer(1, 10))
    
    def _create_enhanced_rebalancing_section(self, analysis_results, current_data, elements):
        """Add enhanced Rebalancing section with charts and detailed actions to PDF"""
        elements.append(Paragraph("⚖️ Enhanced Portfolio Rebalancing", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Strategy description
        elements.append(Paragraph("📊 Recommended Strategy: Balanced", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        strategy_text = "The Balanced strategy allocates: 50% Large Cap (stability), 30% Mid Cap (growth), 20% Small Cap (high growth potential)"
        elements.append(Paragraph(strategy_text, self.styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Current vs Target Allocation
        current_allocation = self._calculate_current_allocation(analysis_results)
        target_allocation = {'Large Cap': 50, 'Mid Cap': 30, 'Small Cap': 20}
        
        # Create comparison chart using matplotlib
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from reportlab.lib.utils import ImageReader
        import numpy as np
        
        categories = list(target_allocation.keys())
        current_values = [current_allocation.get(cat, 0) for cat in categories]
        target_values = [target_allocation[cat] for cat in categories]
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, current_values, width, label='Current Allocation', color='#3498db')
        bars2 = ax.bar(x + width/2, target_values, width, label='Target Allocation', color='#27ae60')
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_title('Current vs Target Allocation', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Category', fontsize=11)
        ax.set_ylabel('Allocation %', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        plt.tight_layout()
        
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
        elements.append(img)
        elements.append(Spacer(1, 5))
        
        # Detailed Rebalancing Actions
        elements.append(Paragraph("📋 Detailed Rebalancing Actions", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        portfolio_value = analysis_results['portfolio_summary']['current_value']
        actions = self._generate_rebalancing_actions(current_allocation, target_allocation, portfolio_value, analysis_results)
        
        if actions:
            actions_data = [['Category', 'Action', 'Amount', 'Description']]
            for action in actions:
                actions_data.append([
                    action['category'],
                    action['action'],
                    f"₹{abs(action['amount']):,.0f}",
                    action['description']
                ])
            
            actions_table = self.create_card_table(actions_data, col_widths=[1.3*inch, 0.8*inch, 1.3*inch, 3.1*inch])
            elements.append(actions_table)
        else:
            elements.append(Paragraph("Your portfolio allocation is well-balanced. No rebalancing needed.", self.styles['Normal']))
        
        elements.append(Spacer(1, 10))
        
        # Implementation Tips
        elements.append(Paragraph("💡 Implementation Tips", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        tips = [
            "• Rebalance gradually over 2-3 months to minimize market timing risk",
            "• Consider tax implications before selling profitable positions",
            "• Use SIP (Systematic Investment Plan) for accumulating new positions",
            "• Review and rebalance quarterly or when allocation drifts by >5%",
            "• Maintain emergency fund before aggressive rebalancing"
        ]
        
        for tip in tips:
            elements.append(Paragraph(tip, self.styles['Normal']))
        
        elements.append(Spacer(1, 10))
    
    def _create_enhanced_customer_profile_section(self, analysis_results, recommendations, elements):
        """Add enhanced Customer Profile section with charts to PDF"""
        elements.append(Paragraph("👤 Enhanced Investment Profile", self.heading_style))
        elements.append(Spacer(1, 10))
        
        summary = analysis_results['portfolio_summary']
        sector_data = pd.DataFrame(analysis_results['sector_analysis'])
        category_data = pd.DataFrame(analysis_results['category_analysis'])
        
        # Investment Style Analysis
        elements.append(Paragraph("📊 Investment Style Analysis", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        # Calculate investment style
        value_count = sum(1 for rec in recommendations if rec.get('value_analysis', {}).get('action') == 'BUY')
        growth_count = sum(1 for rec in recommendations if rec.get('growth_analysis', {}).get('action') == 'BUY')
        
        total_recs = len(recommendations) if recommendations else 1
        value_pct = (value_count / total_recs) * 100
        growth_pct = (growth_count / total_recs) * 100
        balanced_pct = 100 - value_pct - growth_pct if value_pct + growth_pct < 100 else 0
        
        # Investment style pie chart using matplotlib
        if value_pct + growth_pct > 0:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from reportlab.lib.utils import ImageReader
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            values = [value_pct, growth_pct, balanced_pct] if balanced_pct > 0 else [value_pct, growth_pct]
            labels = ['Value', 'Growth', 'Balanced'] if balanced_pct > 0 else ['Value', 'Growth']
            colors = ['#3498db', '#27ae60', '#f39c12'] if balanced_pct > 0 else ['#3498db', '#27ae60']
            
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Investment Style Distribution', fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()
            
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            img = Image(img_bytes, width=5*inch, height=2.6*inch)
            elements.append(img)
            elements.append(Spacer(1, 5))
        
        # Sector Preference Pie Chart using matplotlib
        if not sector_data.empty:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from reportlab.lib.utils import ImageReader
            
            elements.append(Paragraph("🏭 Sector Allocation Preferences", self.subheading_style))
            elements.append(Spacer(1, 10))
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            colors = plt.cm.Pastel1(range(len(sector_data)))
            
            wedges, texts, autotexts = ax.pie(
                sector_data['Current Value'],
                labels=sector_data['Sector'],
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            ax.set_title('Sector Allocation', fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()
            
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            img = Image(img_bytes, width=5*inch, height=2.6*inch)
            elements.append(img)
            elements.append(Spacer(1, 5))
        
        # Market Cap Preference Pie Chart using matplotlib
        if not category_data.empty:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from reportlab.lib.utils import ImageReader
            
            elements.append(Paragraph("📈 Market Cap Allocation", self.subheading_style))
            elements.append(Spacer(1, 10))
            
            fig, ax = plt.subplots(figsize=(6, 3.5))
            
            # Define colors for market caps
            color_map = {'Large Cap': '#2c3e50', 'Mid Cap': '#e67e22', 'Small Cap': '#3498db'}
            colors = [color_map.get(cat, '#95a5a6') for cat in category_data['Category']]
            
            wedges, texts, autotexts = ax.pie(
                category_data['Current Value'],
                labels=category_data['Category'],
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Market Cap Distribution', fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()
            
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
            img_bytes.seek(0)
            plt.close()
            
            img = Image(img_bytes, width=5*inch, height=2.6*inch)
            elements.append(img)
            elements.append(Spacer(1, 5))
        
        # Personalized Strategy Recommendations
        elements.append(Paragraph("💡 Personalized Strategy Recommendations", self.subheading_style))
        elements.append(Spacer(1, 10))
        
        portfolio_size = summary['current_value']
        num_stocks = summary['number_of_stocks']
        
        strategy_recs = []
        if portfolio_size < 500000:
            strategy_recs.append("• Focus on building a core portfolio of 8-10 quality large-cap stocks")
        elif portfolio_size < 2500000:
            strategy_recs.append("• Diversify into mid-cap stocks for enhanced growth potential")
        else:
            strategy_recs.append("• Consider alternative investments and international diversification")
        
        if num_stocks < 8:
            strategy_recs.append("• Increase portfolio diversification to 10-15 stocks across sectors")
        elif num_stocks > 25:
            strategy_recs.append("• Consider consolidating holdings to improve portfolio management")
        
        for rec in strategy_recs:
            elements.append(Paragraph(rec, self.styles['Normal']))
        
        elements.append(Spacer(1, 10))
    
    def _create_historical_performance_charts(self, historical_data, portfolio_data, elements):
        """Add Historical Performance charts to PDF using matplotlib"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from reportlab.lib.utils import ImageReader
        import numpy as np
        
        portfolio_history = self._calculate_portfolio_history(portfolio_data, historical_data)
        
        if portfolio_history.empty:
            return
        
        elements.append(Paragraph("📈 Historical Performance Charts", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Chart 1: Portfolio Value Over Time
        fig, ax = plt.subplots(figsize=(7, 3.5))
        
        ax.plot(portfolio_history['Date'], portfolio_history['Portfolio_Value'], 
               color='#27ae60', linewidth=2, label='Portfolio Value')
        ax.plot(portfolio_history['Date'], portfolio_history['Investment_Value'], 
               color='#3498db', linewidth=2, linestyle='--', label='Investment (Cost Basis)')
        
        ax.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Value (₹)', fontsize=11)
        ax.legend()
        ax.grid(alpha=0.3, linestyle='--')
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
        elements.append(img)
        elements.append(Spacer(1, 8))
        
        # Chart 2: Cumulative Returns
        portfolio_history_copy = portfolio_history.copy()
        portfolio_history_copy['Cumulative_Return'] = ((portfolio_history_copy['Portfolio_Value'] - portfolio_history_copy['Investment_Value']) / portfolio_history_copy['Investment_Value']) * 100
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        colors_ret = ['#27ae60' if x >= 0 else '#e74c3c' for x in portfolio_history_copy['Cumulative_Return']]
        
        ax.bar(portfolio_history_copy['Date'], portfolio_history_copy['Cumulative_Return'], 
              color=colors_ret, width=2)
        
        ax.set_title('Cumulative Returns Over Time', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Return %', fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
        elements.append(img)
        elements.append(Spacer(1, 8))
        
        # Chart 3: Drawdown Analysis
        peak_value = portfolio_history['Portfolio_Value'].expanding().max()
        drawdown = ((portfolio_history['Portfolio_Value'] - peak_value) / peak_value) * 100
        
        fig, ax = plt.subplots(figsize=(7, 3.5))
        
        ax.fill_between(portfolio_history['Date'], drawdown, 0, color='#e74c3c', alpha=0.3)
        ax.plot(portfolio_history['Date'], drawdown, color='#c0392b', linewidth=2)
        
        ax.set_title('Drawdown Analysis (Decline from Peak)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Drawdown %', fontsize=11)
        ax.grid(alpha=0.3, linestyle='--')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=150, bbox_inches='tight')
        img_bytes.seek(0)
        plt.close()
        
        img = Image(img_bytes, width=5.5*inch, height=2.8*inch)
        elements.append(img)
        elements.append(Spacer(1, 5))
    
    def _calculate_portfolio_history(self, portfolio_data, historical_data):
        """Calculate portfolio value over time"""
        import pandas as pd
        import numpy as np
        
        if not historical_data:
            return pd.DataFrame()
        
        # Get earliest buy date
        portfolio_data['Buy Date'] = pd.to_datetime(portfolio_data['Buy Date'])
        start_date = portfolio_data['Buy Date'].min()
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=pd.Timestamp.now(), freq='D')
        
        portfolio_history = pd.DataFrame({'Date': date_range})
        portfolio_history['Portfolio_Value'] = 0.0
        portfolio_history['Investment_Value'] = 0.0
        
        for _, stock in portfolio_data.iterrows():
            stock_name = stock['Stock Name']
            quantity = stock['Quantity']
            buy_price = stock['Buy Price']
            buy_date = stock['Buy Date']
            
            # Get historical data for this stock
            stock_history = historical_data.get(stock_name, pd.DataFrame())
            
            if not stock_history.empty and 'Close' in stock_history.columns:
                # Add stock value for dates after purchase
                for date in portfolio_history['Date']:
                    if date >= buy_date:
                        # Find closest price
                        available_dates = stock_history.index[stock_history.index <= date]
                        if len(available_dates) > 0:
                            closest_date = available_dates[-1]
                            price = stock_history.loc[closest_date, 'Close']
                            
                            idx = portfolio_history[portfolio_history['Date'] == date].index[0]
                            portfolio_history.loc[idx, 'Portfolio_Value'] += quantity * float(price)
                            portfolio_history.loc[idx, 'Investment_Value'] += quantity * buy_price
        
        # Remove rows with zero portfolio value
        portfolio_history = portfolio_history[portfolio_history['Portfolio_Value'] > 0]
        
        return portfolio_history
    
    def _calculate_current_allocation(self, analysis_results):
        """Calculate current allocation by category"""
        category_analysis = pd.DataFrame(analysis_results['category_analysis'])
        
        if category_analysis.empty:
            return {}
        
        allocation = {}
        for _, cat in category_analysis.iterrows():
            allocation[cat['Category']] = cat['Percentage of Portfolio']
        
        return allocation
    
    def _generate_rebalancing_actions(self, current_allocation, target_allocation, portfolio_value, analysis_results):
        """Generate rebalancing actions"""
        actions = []
        
        for category, target_pct in target_allocation.items():
            current_pct = current_allocation.get(category, 0)
            diff_pct = target_pct - current_pct
            
            if abs(diff_pct) > 2:  # Only suggest if difference > 2%
                amount = (diff_pct / 100) * portfolio_value
                
                if diff_pct > 0:
                    action = {
                        'category': category,
                        'action': 'BUY',
                        'amount': amount,
                        'description': f"Increase {category} allocation by {diff_pct:.1f}%"
                    }
                else:
                    action = {
                        'category': category,
                        'action': 'SELL',
                        'amount': amount,
                        'description': f"Reduce {category} allocation by {abs(diff_pct):.1f}%"
                    }
                
                actions.append(action)
        
        # Sort by absolute amount (largest first)
        actions.sort(key=lambda x: abs(x['amount']), reverse=True)
        
        return actions
    
    def _calculate_health_score(self, analysis_results, recommendations):
        """Calculate portfolio health score (0-100)"""
        score = 0
        
        # Performance (25 points)
        portfolio_return = analysis_results['portfolio_summary']['total_gain_loss_percentage']
        if portfolio_return > 25:
            score += 25
        elif portfolio_return > 10:
            score += 20
        elif portfolio_return > 0:
            score += 15
        elif portfolio_return > -10:
            score += 10
        else:
            score += 5
        
        # Diversification (25 points)
        num_stocks = analysis_results['portfolio_summary']['number_of_stocks']
        sector_count = len(analysis_results['sector_analysis'])
        
        if num_stocks >= 15 and sector_count >= 5:
            score += 25
        elif num_stocks >= 10 and sector_count >= 4:
            score += 20
        elif num_stocks >= 6 and sector_count >= 3:
            score += 15
        else:
            score += 10
        
        # Profitable Holdings (25 points)
        profitable_pct = (analysis_results['portfolio_summary']['profitable_stocks'] / 
                         analysis_results['portfolio_summary']['number_of_stocks'] * 100)
        
        if profitable_pct >= 80:
            score += 25
        elif profitable_pct >= 60:
            score += 20
        elif profitable_pct >= 40:
            score += 15
        else:
            score += 10
        
        # Investment Strategy Alignment (25 points)
        buy_recs = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'BUY')
        sell_recs = sum(1 for rec in recommendations if rec['overall_recommendation']['action'] == 'SELL')
        
        if sell_recs == 0 and buy_recs > 0:
            score += 25
        elif sell_recs <= 2:
            score += 20
        elif sell_recs <= 4:
            score += 15
        else:
            score += 10
        
        return min(score, 100)
    
    def _create_dividend_section(self, dividend_metrics, elements):
        """Add Dividend Yield Metrics section to PDF"""
        if not dividend_metrics:
            dividend_metrics = {
                'portfolio_dividend_yield': 0,
                'total_annual_dividend': 0,
                'highest_yield_stock': 'N/A',
                'highest_yield_value': 0,
                'dividend_paying_stocks': 0,
                'non_dividend_stocks': 0
            }
        
        elements.append(Paragraph("💰 Dividend Yield Metrics", self.heading_style))
        elements.append(Spacer(1, 10))
        
        portfolio_yield = dividend_metrics.get('portfolio_dividend_yield', 0)
        annual_dividend = dividend_metrics.get('total_annual_dividend', 0)
        highest_yield_stock = dividend_metrics.get('highest_yield_stock', 'N/A')
        highest_yield_value = dividend_metrics.get('highest_yield_value', 0)
        dividend_stocks = dividend_metrics.get('dividend_paying_stocks', 0)
        non_dividend = dividend_metrics.get('non_dividend_stocks', 0)
        
        dividend_data = [
            ['Metric', 'Value', 'Description'],
            ['Portfolio Dividend Yield', f"{portfolio_yield:.2f}%", 'Weighted average dividend yield'],
            ['Expected Annual Dividend', f"₹{annual_dividend:,.0f}", 'Projected yearly dividend income'],
            ['Dividend-Paying Stocks', f"{dividend_stocks}", 'Stocks currently paying dividends'],
            ['Non-Dividend Stocks', f"{non_dividend}", 'Stocks not paying dividends'],
            ['Highest Yield Stock', f"{highest_yield_stock}", f"Yield: {highest_yield_value:.2f}%"]
        ]
        
        dividend_table = self.create_card_table(
            dividend_data,
            col_widths=[2.2*inch, 1.5*inch, 2.8*inch],
            header_color=colors.HexColor('#27ae60')
        )
        elements.append(dividend_table)
        elements.append(Spacer(1, 15))
    
    def _create_tax_section(self, tax_data, analysis_results, elements):
        """Add Tax Implications section to PDF"""
        from utils.advanced_metrics import AdvancedMetricsCalculator
        
        # Calculate tax data if not provided
        if not tax_data:
            try:
                calculator = AdvancedMetricsCalculator()
                stock_df = pd.DataFrame(analysis_results.get('stock_performance', []))
                if not stock_df.empty:
                    tax_data = calculator.calculate_tax_impact(stock_df)
                else:
                    tax_data = self._get_default_tax_data()
            except:
                tax_data = self._get_default_tax_data()
        
        elements.append(Paragraph("📋 Tax Implications (If Portfolio Sold Today)", self.heading_style))
        elements.append(Spacer(1, 10))
        
        # Main tax metrics
        tax_metrics_data = [
            ['Tax Category', 'Amount', 'Rate/Notes'],
            ['Short-Term Capital Gains (STCG)', f"₹{tax_data.get('short_term_gains', 0):,.0f}", 'Holdings < 1 year'],
            ['Long-Term Capital Gains (LTCG)', f"₹{tax_data.get('long_term_gains', 0):,.0f}", 'Holdings ≥ 1 year'],
            ['Estimated STCG Tax', f"₹{tax_data.get('estimated_stcg_tax', 0):,.0f}", '20% flat rate'],
            ['Estimated LTCG Tax', f"₹{tax_data.get('estimated_ltcg_tax', 0):,.0f}", '12.5% above ₹1.25L exemption'],
            ['Total Estimated Tax', f"₹{tax_data.get('total_estimated_tax', 0):,.0f}", 'Combined tax liability']
        ]
        
        tax_table = self.create_card_table(
            tax_metrics_data,
            col_widths=[2.5*inch, 1.8*inch, 2.2*inch],
            header_color=colors.HexColor('#e74c3c')
        )
        elements.append(tax_table)
        elements.append(Spacer(1, 12))
        
        # Transaction costs
        elements.append(Paragraph("Transaction Costs & Charges", self.subheading_style))
        elements.append(Spacer(1, 8))
        
        transaction_data = [
            ['Charge Type', 'Amount', 'Rate'],
            ['Securities Transaction Tax (STT)', f"₹{tax_data.get('stt_on_sell', 0):,.0f}", '0.1% on sell value'],
            ['Stamp Duty', f"₹{tax_data.get('stamp_duty', 0):,.0f}", '0.015% on buy value'],
            ['Exchange Transaction Charges', f"₹{tax_data.get('transaction_charges', 0):,.0f}", '0.00345%'],
            ['SEBI Turnover Fee', f"₹{tax_data.get('sebi_charges', 0):,.0f}", '0.0001%'],
            ['Total Transaction Costs', f"₹{tax_data.get('total_transaction_costs', 0):,.0f}", 'All charges combined']
        ]
        
        transaction_table = self.create_card_table(
            transaction_data,
            col_widths=[2.5*inch, 1.8*inch, 2.2*inch],
            header_color=colors.HexColor('#9b59b6')
        )
        elements.append(transaction_table)
        elements.append(Spacer(1, 10))
        
        # Tax disclaimer
        tax_disclaimer = Paragraph(
            "<i>Note: Tax calculations are estimates based on Union Budget 2024 rates. LTCG exemption of ₹1.25 lakh applies annually. "
            "Consult a qualified tax advisor for personalized advice.</i>",
            ParagraphStyle('TaxDisclaimer', parent=self.styles['Normal'], fontSize=9, textColor=colors.grey)
        )
        elements.append(tax_disclaimer)
        elements.append(Spacer(1, 15))
    
    def _get_default_tax_data(self):
        """Return default tax data structure"""
        return {
            'short_term_gains': 0,
            'long_term_gains': 0,
            'estimated_stcg_tax': 0,
            'estimated_ltcg_tax': 0,
            'total_estimated_tax': 0,
            'stt_on_sell': 0,
            'stamp_duty': 0,
            'transaction_charges': 0,
            'sebi_charges': 0,
            'total_transaction_costs': 0
        }
