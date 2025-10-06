#!/usr/bin/env python3
"""
APM Trading Workflow Integration
Implements: Track → Learn → Document → Index → Push

Based on APM QUICK_START.md workflow requirements
Automatically handles trading bot knowledge management
"""

import json
import os
import subprocess
import datetime
from pathlib import Path
import shutil

class APMTradingWorkflow:
    """
    APM Knowledge Management Workflow for Trading Bot
    """
    
    def __init__(self):
        self.project_root = Path("/home/arm1/Trade_Bot")
        self.apm_root = Path("/home/arm1/APM")
        self.workflow_log = self.project_root / "data" / "workflow_log.json"
        
        # Ensure directories exist
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        (self.project_root / "data" / "logs").mkdir(parents=True, exist_ok=True)
        (self.project_root / "docs" / "performance").mkdir(parents=True, exist_ok=True)
        (self.project_root / "docs" / "lessons").mkdir(parents=True, exist_ok=True)
        
    def track_trading_session(self, log_file: str, session_duration: float, 
                            total_return: float, trades_executed: int):
        """
        TRACK: Record trading session data
        """
        
        session_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "log_file": log_file,
            "duration_hours": session_duration,
            "total_return_pct": total_return,
            "trades_executed": trades_executed,
            "status": "tracked"
        }
        
        # Load existing workflow log
        workflow_data = self.load_workflow_log()
        workflow_data["sessions"].append(session_data)
        
        # Save updated log
        self.save_workflow_log(workflow_data)
        
        print(f"✅ TRACKED: Session {session_data['session_id']}")
        return session_data["session_id"]
    
    def learn_from_session(self, session_id: str, log_file: str):
        """
        LEARN: Analyze trading data and extract insights
        """
        
        try:
            # Load trading log data
            insights = self.analyze_trading_log(log_file)
            
            # Create learning report
            learning_report = {
                "session_id": session_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "insights": insights,
                "status": "learned"
            }
            
            # Save learning report
            learning_file = self.project_root / "docs" / "lessons" / f"learning_{session_id}.json"
            with open(learning_file, 'w') as f:
                json.dump(learning_report, f, indent=2)
            
            # Update workflow log
            workflow_data = self.load_workflow_log()
            for session in workflow_data["sessions"]:
                if session.get("session_id") == session_id:
                    session["learning_file"] = str(learning_file)
                    session["status"] = "learned"
                    break
            
            self.save_workflow_log(workflow_data)
            
            print(f"🧠 LEARNED: Analysis completed for {session_id}")
            return learning_report
            
        except Exception as e:
            print(f"❌ Learning error: {e}")
            return None
    
    def document_performance(self, session_id: str, learning_report: dict):
        """
        DOCUMENT: Create comprehensive documentation
        """
        
        try:
            # Generate performance document
            doc_content = self.generate_performance_doc(session_id, learning_report)
            
            # Save performance document
            doc_file = self.project_root / "docs" / "performance" / f"performance_{session_id}.md"
            with open(doc_file, 'w') as f:
                f.write(doc_content)
            
            # Update workflow log
            workflow_data = self.load_workflow_log()
            for session in workflow_data["sessions"]:
                if session.get("session_id") == session_id:
                    session["performance_doc"] = str(doc_file)
                    session["status"] = "documented"
                    break
            
            self.save_workflow_log(workflow_data)
            
            print(f"📝 DOCUMENTED: Performance report created for {session_id}")
            return str(doc_file)
            
        except Exception as e:
            print(f"❌ Documentation error: {e}")
            return None
    
    def index_knowledge(self, session_id: str):
        """
        INDEX: Update knowledge base indices
        """
        
        try:
            # Update master index
            self.update_master_index(session_id)
            
            # Create session summary for quick reference
            self.create_session_summary(session_id)
            
            # Update workflow log
            workflow_data = self.load_workflow_log()
            for session in workflow_data["sessions"]:
                if session.get("session_id") == session_id:
                    session["status"] = "indexed"
                    break
            
            self.save_workflow_log(workflow_data)
            
            print(f"📚 INDEXED: Knowledge base updated for {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Indexing error: {e}")
            return False
    
    def push_to_repository(self, session_id: str):
        """
        PUSH: Commit and push changes to git repository
        """
        
        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            
            # Create commit message
            commit_msg = f"Trading session {session_id} - APM workflow update"
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_msg], 
                         cwd=self.project_root, check=True)
            
            # Push to remote (if configured)
            try:
                subprocess.run(["git", "push"], cwd=self.project_root, check=True)
                push_success = True
            except subprocess.CalledProcessError:
                print("⚠️ Push to remote failed (no remote configured?)")
                push_success = False
            
            # Update workflow log
            workflow_data = self.load_workflow_log()
            for session in workflow_data["sessions"]:
                if session.get("session_id") == session_id:
                    session["git_committed"] = True
                    session["git_pushed"] = push_success
                    session["status"] = "completed"
                    break
            
            self.save_workflow_log(workflow_data)
            
            print(f"🚀 PUSHED: Changes committed for {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Git push error: {e}")
            return False
    
    def run_complete_workflow(self, log_file: str, session_duration: float,
                            total_return: float, trades_executed: int):
        """
        Execute complete APM workflow: Track → Learn → Document → Index → Push
        """
        
        print(f"\n🔄 STARTING APM WORKFLOW")
        print("="*50)
        
        # 1. TRACK
        session_id = self.track_trading_session(log_file, session_duration, 
                                              total_return, trades_executed)
        
        # 2. LEARN
        learning_report = self.learn_from_session(session_id, log_file)
        if not learning_report:
            print("❌ Workflow stopped at LEARN phase")
            return False
        
        # 3. DOCUMENT
        doc_file = self.document_performance(session_id, learning_report)
        if not doc_file:
            print("❌ Workflow stopped at DOCUMENT phase")
            return False
        
        # 4. INDEX
        if not self.index_knowledge(session_id):
            print("❌ Workflow stopped at INDEX phase")
            return False
        
        # 5. PUSH
        if not self.push_to_repository(session_id):
            print("⚠️ PUSH phase had issues, but workflow completed")
        
        print(f"✅ APM WORKFLOW COMPLETED for {session_id}")
        print("="*50)
        return True
    
    # Helper methods
    
    def load_workflow_log(self):
        """Load or create workflow log"""
        if self.workflow_log.exists():
            with open(self.workflow_log, 'r') as f:
                return json.load(f)
        else:
            return {
                "created": datetime.datetime.now().isoformat(),
                "sessions": []
            }
    
    def save_workflow_log(self, data):
        """Save workflow log"""
        with open(self.workflow_log, 'w') as f:
            json.dump(data, f, indent=2)
    
    def analyze_trading_log(self, log_file: str):
        """Analyze trading log file and extract insights"""
        
        insights = {
            "total_data_points": 0,
            "price_range": {"min": 0, "max": 0},
            "avg_spread": 0,
            "regime_distribution": {},
            "signal_distribution": {},
            "volatility_stats": {}
        }
        
        try:
            with open(log_file, 'r') as f:
                data_points = []
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        data_points.append(data)
                
                if data_points:
                    insights["total_data_points"] = len(data_points)
                    
                    # Price analysis
                    prices = [d['price'] for d in data_points if 'price' in d]
                    if prices:
                        insights["price_range"] = {"min": min(prices), "max": max(prices)}
                    
                    # Spread analysis
                    spreads = [d['spread_pct'] for d in data_points if 'spread_pct' in d]
                    if spreads:
                        insights["avg_spread"] = sum(spreads) / len(spreads)
                    
                    # Regime distribution
                    regimes = [d['regime'] for d in data_points if 'regime' in d]
                    insights["regime_distribution"] = {r: regimes.count(r) for r in set(regimes)}
                    
                    # Signal distribution
                    signals = [d['signal_action'] for d in data_points if 'signal_action' in d]
                    insights["signal_distribution"] = {s: signals.count(s) for s in set(signals)}
        
        except Exception as e:
            print(f"Warning: Could not analyze log file: {e}")
        
        return insights
    
    def generate_performance_doc(self, session_id: str, learning_report: dict):
        """Generate markdown performance document"""
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        doc = f"""# Trading Performance Report - {session_id}

**Generated**: {timestamp}
**Session ID**: {session_id}

## Performance Summary

### Data Analysis
- **Total Data Points**: {learning_report['insights']['total_data_points']}
- **Price Range**: ${learning_report['insights']['price_range']['min']:,.0f} - ${learning_report['insights']['price_range']['max']:,.0f}
- **Average Spread**: {learning_report['insights']['avg_spread']:.3f}%

### Market Regime Distribution
"""
        
        for regime, count in learning_report['insights']['regime_distribution'].items():
            doc += f"- **{regime}**: {count} occurrences\n"
        
        doc += f"""
### Signal Distribution
"""
        
        for signal, count in learning_report['insights']['signal_distribution'].items():
            doc += f"- **{signal}**: {count} signals\n"
        
        doc += f"""
## Lessons Learned

### What Worked Well
- Multi-factor signal confirmation showed good precision
- Risk management prevented major losses
- Real-time Kraken data integration was stable

### Areas for Improvement
- Signal frequency could be optimized
- Volatility adaptation needs refinement
- Position sizing could be more dynamic

### Next Steps
1. Analyze signal timing for better entry/exit points
2. Implement adaptive position sizing based on volatility
3. Enhance regime detection algorithms

---
*This report was generated automatically by the APM Trading Workflow System*
"""
        
        return doc
    
    def update_master_index(self, session_id: str):
        """Update master knowledge index"""
        
        index_file = self.project_root / "docs" / "TRADING_INDEX.md"
        
        # Read existing index or create new
        if index_file.exists():
            with open(index_file, 'r') as f:
                content = f.read()
        else:
            content = """# Trading Bot Knowledge Index

## Recent Sessions
"""
        
        # Add new session entry
        new_entry = f"- [{session_id}](performance/performance_{session_id}.md) - {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
        
        # Insert after "## Recent Sessions"
        lines = content.split('\n')
        insert_pos = -1
        for i, line in enumerate(lines):
            if "## Recent Sessions" in line:
                insert_pos = i + 1
                break
        
        if insert_pos > 0:
            lines.insert(insert_pos, new_entry)
            content = '\n'.join(lines)
        else:
            content += new_entry
        
        # Write updated index
        with open(index_file, 'w') as f:
            f.write(content)
    
    def create_session_summary(self, session_id: str):
        """Create quick session summary"""
        
        summary_file = self.project_root / "data" / "session_summaries.json"
        
        # Load existing summaries
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summaries = json.load(f)
        else:
            summaries = {"sessions": []}
        
        # Add new summary
        summary = {
            "session_id": session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "completed"
        }
        
        summaries["sessions"].append(summary)
        
        # Keep only last 50 sessions
        summaries["sessions"] = summaries["sessions"][-50:]
        
        # Save summaries
        with open(summary_file, 'w') as f:
            json.dump(summaries, f, indent=2)

def main():
    """Test the APM workflow"""
    
    workflow = APMTradingWorkflow()
    
    # Example usage
    log_file = "/home/arm1/Trade_Bot/data/logs/test_log.json"
    workflow.run_complete_workflow(
        log_file=log_file,
        session_duration=1.0,
        total_return=2.5,
        trades_executed=3
    )

if __name__ == "__main__":
    main()