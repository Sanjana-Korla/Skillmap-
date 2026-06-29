import io 
import html
from reportlab.lib.pagesizes import letter 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle 
from reportlab.lib import colors 

class PDFExporter: 
    @staticmethod 
    def export_roadmap_to_pdf(target_role: str, gap_report: dict, roadmap_data: dict) -> bytes: 
        buffer = io.BytesIO() 
        doc = SimpleDocTemplate( 
            buffer, 
            pagesize=letter, 
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40 
        ) 
        styles = getSampleStyleSheet() 
        primary_color = colors.HexColor("#1A2B4C") 
        dark_text = colors.HexColor("#333333") 
        title_style = ParagraphStyle( 
            'DocTitle', 
            parent=styles['Heading1'], 
            fontName='Helvetica-Bold', 
            fontSize=22, 
            textColor=primary_color, 
            spaceAfter=10 
        ) 
        section_style = ParagraphStyle( 
            'SectionHeader', 
            parent=styles['Heading2'], 
            fontName='Helvetica-Bold', 
            fontSize=14, 
            textColor=primary_color, 
            spaceBefore=12, 
            spaceAfter=8 
        ) 
        body_style = ParagraphStyle( 
            'BodyTextCustom', 
            parent=styles['Normal'], 
            fontName='Helvetica', 
            fontSize=9, 
            textColor=dark_text, 
            leading=13 
        ) 
        story = [] 
        story.append(Paragraph(f"SkillMap Career Acceleration Blueprint", title_style)) 
        story.append(Paragraph(f"<b>Target Role:</b> {html.escape(target_role)}", body_style)) 
        story.append(Paragraph(f"<b>Core Skill Match Rating:</b> {gap_report.get('match_score', 0.0)}%", body_style)) 
        story.append(Spacer(1, 15)) 
        story.append(Paragraph("Identified Skill Gaps", section_style)) 
        
        missing_skills_str = ", ".join([html.escape(m["skill"]) for m in gap_report.get("missing_skills", [])]) 
        weak_skills_str = ", ".join([html.escape(w["skill"]) for w in gap_report.get("weak_skills", [])]) 
        story.append(Paragraph(f"<b>Primary Missing Skills:</b> {missing_skills_str if missing_skills_str else 'None'}", body_style)) 
        story.append(Spacer(1, 5)) 
        story.append(Paragraph(f"<b>Weak Skills to Polish:</b> {weak_skills_str if weak_skills_str else 'None'}", body_style)) 
        story.append(Spacer(1, 15)) 
        story.append(Paragraph("Structured Curriculum Strategy", section_style)) 
        
        roadmap_title = roadmap_data.get("roadmap_title", "Custom Acceleration Program") 
        story.append(Paragraph(f"<b>Curriculum Track:</b> {html.escape(roadmap_title)}", body_style)) 
        story.append(Spacer(1, 10)) 
        
        table_data = [[ 
            Paragraph("<b>Week</b>", body_style), 
            Paragraph("<b>Target Skills & Topics</b>", body_style), 
            Paragraph("<b>Outcome Goals & Resources</b>", body_style) 
        ]] 
        
        for week in roadmap_data.get("weeks", []): 
            week_num = f"Week {week.get('week_number')}" 
            
            # Escape strings to prevent XML errors inside tables
            escaped_skills = [html.escape(s) for s in week.get('focus_skills', [])]
            escaped_topics = [html.escape(t) for t in week.get('topics', [])]
            
            skills_n_topics = f"<b>Skills:</b> {', '.join(escaped_skills)}<br/><br/><b>Topics:</b> {', '.join(escaped_topics)}" 
            
            resources_list = week.get('resources', []) 
            resources_str = "" 
            if resources_list: 
                resources_str = "<br/><br/><b>Recommended Learning Resources:</b>" 
                for r in resources_list: 
                    safe_title = html.escape(r.get('title', ''))
                    safe_platform = html.escape(r.get('platform', ''))
                    safe_url = html.escape(r.get('url', ''))
                    resources_str += f"<br/>• {safe_title} ({safe_platform}): {safe_url}" 
            
            safe_goal = html.escape(week.get('curriculum_goal', ''))
            safe_outcome = html.escape(week.get('expected_outcome', ''))
            goals = f"<b>Objective:</b> {safe_goal}<br/><br/><b>Expected Outcome:</b> {safe_outcome}{resources_str}" 
            
            table_data.append([ 
                Paragraph(week_num, body_style), 
                Paragraph(skills_n_topics, body_style), 
                Paragraph(goals, body_style) 
            ]) 
            
        col_widths = [50, 200, 280] 
        t = Table(table_data, colWidths=col_widths) 
        t.setStyle(TableStyle([ 
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F2F2")), 
            ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
            ('VALIGN', (0,0), (-1,-1), 'TOP'), 
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey), 
            ('TOPPADDING', (0,0), (-1,-1), 6), 
            ('BOTTOMPADDING', (0,0), (-1,-1), 6), 
        ])) 
        story.append(t) 
        doc.build(story) 
        buffer.seek(0) 
        return buffer.getvalue()