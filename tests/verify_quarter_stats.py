import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, select
from app.services import report_service
from app.models.user import User, Role
from app.models.report import Report

# Setup DB connection
sqlite_url = f"sqlite:///data/app.db"
engine = create_engine(sqlite_url)

def verify_quarter_stats():
    with Session(engine) as session:
        print("Verifying get_zzs_report_stats with quarter=1...")
        stats = report_service.get_zzs_report_stats(session, year=2025, quarter=1)
        
        print(f"Stats returned keys: {stats.keys()}")
        print(f"Quarter in stats: {stats.get('quarter')}")
        print(f"Overall stats: {stats.get('overall')}")
        
        if stats.get('quarter') == 1:
            print("SUCCESS: Quarter parameter is correctly returned.")
        else:
            print("FAILURE: Quarter parameter is missing or incorrect.")

        print("-" * 20)
        
        # Verify filtering logic (basic check)
        # Check if any reports in result are outside the quarter?
        # The service returns aggregate stats, not raw reports.
        # But we can check if the count matches a manual query if needed.
        # For now, just ensuring it runs without error and accepts the parameter is good.

        print("Verifying get_zhibu_report_stats with quarter=1...")
        # Get a valid zhibu first
        zhibu = session.exec(select(User.zhibu).where(User.zhibu != None).limit(1)).first()
        if zhibu:
            zhibu_stats = report_service.get_zhibu_report_stats(session, zhibu=zhibu, year=2025, quarter=1)
            print(f"Zhibu stats for {zhibu}: {zhibu_stats.keys()}")
            print("SUCCESS: get_zhibu_report_stats executed successfully.")
        else:
            print("WARNING: No zhibu found to test get_zhibu_report_stats.")

if __name__ == "__main__":
    verify_quarter_stats()
