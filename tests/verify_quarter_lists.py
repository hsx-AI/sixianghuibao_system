
import sys
import os
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session, select, func
from app.database import engine
from app.models.user import User, Role
from app.models.report import Report, ReportStatus, CurrentStep
from app.services import report_service

def verify_quarter_lists():
    with Session(engine) as session:
        # 1. Setup test data
        # Create a test user (Activist)
        activist = session.exec(select(User).where(User.real_name == "TestActivistQuarter")).first()
        if not activist:
            activist = User(
                username="test_activist_quarter",
                password_hash="hash",
                real_name="TestActivistQuarter",
                role=Role.ACTIVIST,
                zhibu="TestZhibu"
            )
            session.add(activist)
            session.commit()
            session.refresh(activist)
        
        # Create a test reviewer (ZBSJ)
        reviewer = session.exec(select(User).where(User.real_name == "TestReviewerQuarter")).first()
        if not reviewer:
            reviewer = User(
                username="test_reviewer_quarter",
                password_hash="hash",
                real_name="TestReviewerQuarter",
                role=Role.ZBSJ,
                zhibu="TestZhibu"
            )
            session.add(reviewer)
            session.commit()
            session.refresh(reviewer)

        # Create reports for Q1 (Jan), Q1 (Mar), Q2 (Apr)
        current_year = datetime.now().year
        
        # Report 1: Q1 (Jan)
        report1 = session.exec(select(Report).where(
            Report.user_id == activist.id, 
            Report.year == current_year, 
            Report.month == 1
        )).first()
        if not report1:
            report1 = Report(
                user_id=activist.id,
                year=current_year,
                month=1,
                file_path="test_q1_1.docx",
                title="Q1 Report 1",
                uploaded_time=datetime.now(),
                current_step=CurrentStep.ZBSJ, # Assign to ZBSJ for list_pending verification
                status=ReportStatus.PENDING
            )
            session.add(report1)
        
        # Report 2: Q1 (Mar)
        report2 = session.exec(select(Report).where(
            Report.user_id == activist.id, 
            Report.year == current_year, 
            Report.month == 3
        )).first()
        if not report2:
            report2 = Report(
                user_id=activist.id,
                year=current_year,
                month=3,
                file_path="test_q1_2.docx",
                title="Q1 Report 2",
                uploaded_time=datetime.now(),
                current_step=CurrentStep.ZBSJ,
                status=ReportStatus.PENDING
            )
            session.add(report2)
            
        # Report 3: Q2 (Apr)
        report3 = session.exec(select(Report).where(
            Report.user_id == activist.id, 
            Report.year == current_year, 
            Report.month == 4
        )).first()
        if not report3:
            report3 = Report(
                user_id=activist.id,
                year=current_year,
                month=4,
                file_path="test_q2_1.docx",
                title="Q2 Report 1",
                uploaded_time=datetime.now(),
                current_step=CurrentStep.ZBSJ,
                status=ReportStatus.PENDING
            )
            session.add(report3)
        
        session.commit()
        
        print("Test data setup complete.")

        # 2. Verify list_zhibu_reports with quarter
        print("\nVerifying list_zhibu_reports (Quarter 1)...")
        q1_reports = report_service.list_zhibu_reports(
            session, 
            zhibu="TestZhibu", 
            year=current_year, 
            quarter=1
        )
        print(f"Found {len(q1_reports)} reports for Q1.")
        
        q1_ids = [r.id for r in q1_reports]
        if report1.id in q1_ids and report2.id in q1_ids and report3.id not in q1_ids:
            print("SUCCESS: list_zhibu_reports correctly filtered Q1 reports.")
        else:
            print(f"FAILURE: list_zhibu_reports returned incorrect reports: {q1_ids}")
            print(f"Expected: {[report1.id, report2.id]}")

        print("\nVerifying list_zhibu_reports (Quarter 2)...")
        q2_reports = report_service.list_zhibu_reports(
            session, 
            zhibu="TestZhibu", 
            year=current_year, 
            quarter=2
        )
        print(f"Found {len(q2_reports)} reports for Q2.")
        q2_ids = [r.id for r in q2_reports]
        if report3.id in q2_ids and report1.id not in q2_ids:
             print("SUCCESS: list_zhibu_reports correctly filtered Q2 reports.")
        else:
             print(f"FAILURE: list_zhibu_reports returned incorrect reports: {q2_ids}")

        # 3. Verify list_pending_reports_for_reviewer with quarter
        print("\nVerifying list_pending_reports_for_reviewer (Quarter 1)...")
        # Since we set current_step=ZBSJ and reviewer is ZBSJ, these should show up
        pending_q1 = report_service.list_pending_reports_for_reviewer(
            session,
            reviewer=reviewer,
            year=current_year,
            quarter=1
        )
        print(f"Found {len(pending_q1)} pending reports for Q1.")
        pending_q1_ids = [r.id for r in pending_q1]
        
        # Filter to our test reports only
        test_pending_q1 = [rid for rid in pending_q1_ids if rid in [report1.id, report2.id, report3.id]]
        
        if report1.id in test_pending_q1 and report2.id in test_pending_q1 and report3.id not in test_pending_q1:
            print("SUCCESS: list_pending_reports_for_reviewer correctly filtered Q1 reports.")
        else:
            print(f"FAILURE: list_pending_reports_for_reviewer returned incorrect reports: {test_pending_q1}")

        # Cleanup (optional, or rely on test DB)
        # session.delete(report1)
        # session.delete(report2)
        # session.delete(report3)
        # session.delete(activist)
        # session.delete(reviewer)
        # session.commit()

if __name__ == "__main__":
    verify_quarter_lists()
