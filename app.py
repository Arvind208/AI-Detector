"""
AI Sentinel - AI Text Detector
Entry point CLI and Web Application Runner
Authored by Arvind (https://github.com/Arvind208)

Usage:
  1. Launch Web Server:
     python app.py
     python app.py --serve --port 8000

  2. Run CLI Detection:
     python app.py --text "Your text to analyze here..."
     python app.py --file document.txt
"""

import argparse
import json
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def run_cli_detection(text: str):
    from src.ai_detector.engine import analyze_text
    
    print("\n" + "=" * 60)
    print(" [AI SENTINEL] TEXT ANALYSIS REPORT")
    print("=" * 60)
    
    result = analyze_text(text)
    if "error" in result:
        print(f"❌ Error: {result['error']}\n")
        sys.exit(1)
        
    score = result["score"]
    verdict = result["verdict"]
    metrics = result["metrics"]
    
    # Progress bar indicator
    bar_filled = int(score / 5)
    bar = "#" * bar_filled + "-" * (20 - bar_filled)
    
    print(f"\nAI Probability: [{bar}] {score}%")
    print(f"Verdict:        {verdict}")
    print(f"Summary:        {result['summary']}")
    print("-" * 60)
    print("Core Metrics:")
    print(f"   * Word Count:         {metrics['word_count']}")
    print(f"   * Sentence Count:     {metrics['sentence_count']}")
    print(f"   * Burstiness (CV):    {metrics['burstiness']} -> {metrics['burstiness_label']}")
    print(f"   * Perplexity Index:   {metrics['perplexity']} -> {metrics['perplexity_label']}")
    print(f"   * Lexical Diversity:  {metrics['ttr']} (TTR)")
    print(f"   * Reading Ease:       {metrics['reading_ease']} / 100")
    
    if metrics["detected_markers"]:
        print(f"   * AI Marker Phrases:  {', '.join(metrics['detected_markers'])}")
        
    print("\nSentence Breakdown:")
    for i, s in enumerate(result["sentences"][:5], 1):
        status_tag = "[AI]" if s["score"] >= 70 else ("[MIX]" if s["score"] >= 40 else "[HUM]")
        print(f"   {status_tag} [{s['score']}%] Sent {i}: \"{s['sentence'][:65]}...\"")
        
    if len(result["sentences"]) > 5:
        print(f"   ... and {len(result['sentences']) - 5} more sentences analyzed.")
        
    print("\n" + "=" * 60 + "\n")


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    import uvicorn
    
    print(f"\n🚀 Starting AI Sentinel Web Server on http://{host}:{port}")
    print(f"📖 Swagger API Docs available at http://{host}:{port}/docs")
    print(f"👤 Developed by Arvind (https://github.com/Arvind208)\n")
    
    uvicorn.run("src.ai_detector.api:app", host=host, port=port, reload=reload)


def main():
    parser = argparse.ArgumentParser(
        description="AI Sentinel - Multi-Signal AI Text Detector by Arvind (@Arvind208)"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Text string to evaluate directly via CLI"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to text file to evaluate"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the FastAPI web server and UI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the web server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for the server (default: 127.0.0.1)"
    )

    args = parser.parse_args()

    if args.text:
        run_cli_detection(args.text)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
        run_cli_detection(text)
    else:
        # Default behavior: run server
        run_server(host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
