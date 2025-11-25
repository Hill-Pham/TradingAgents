"""
Visualize the TradingAgents workflow graph structure.
This script generates a visual representation of the agent workflow.
"""

import os

def visualize_trading_graph(selected_analysts=["market", "social", "news"]):
    """
    Generate a Mermaid diagram showing the trading agents workflow.
    
    Args:
        selected_analysts: List of analysts to include in the graph
    """
    
    # Start Mermaid diagram
    mermaid = ["graph TD"]
    mermaid.append("    Start([START])")
    
    # Analyst nodes
    analyst_colors = {
        "market": "style Market fill:#e1f5ff",
        "social": "style Social fill:#fff3e0", 
        "news": "style News fill:#f3e5f5"
    }
    
    # Add analyst chain
    for i, analyst in enumerate(selected_analysts):
        analyst_cap = analyst.capitalize()
        analyst_name = f"{analyst_cap}"
        tools_name = f"Tools_{analyst_cap}"
        clear_name = f"Clear_{analyst_cap}"
        
        # Add nodes
        mermaid.append(f"    {analyst_name}[{analyst_cap} Analyst]")
        mermaid.append(f"    {tools_name}{{{{Use Tools}}}}")
        mermaid.append(f"    {clear_name}[Clear Messages]")
        
        # Connect from Start or previous analyst
        if i == 0:
            mermaid.append(f"    Start --> {analyst_name}")
        else:
            prev_analyst = selected_analysts[i-1].capitalize()
            mermaid.append(f"    Clear_{prev_analyst} --> {analyst_name}")
        
        # Conditional edge
        mermaid.append(f"    {analyst_name} -->|Need Tools?| {tools_name}")
        mermaid.append(f"    {analyst_name} -->|Done| {clear_name}")
        mermaid.append(f"    {tools_name} --> {analyst_name}")
    
    # Research phase
    last_analyst = selected_analysts[-1].capitalize()
    mermaid.append(f"    Clear_{last_analyst} --> Bull")
    mermaid.append("    Bull[Bull Researcher]")
    mermaid.append("    Bear[Bear Researcher]")
    mermaid.append("    Manager[Research Manager]")
    
    mermaid.append("    Bull -->|Counter?| Bear")
    mermaid.append("    Bull -->|Consensus| Manager")
    mermaid.append("    Bear -->|Counter?| Bull")
    mermaid.append("    Bear -->|Consensus| Manager")
    
    # Trading phase
    mermaid.append("    Manager --> Trader")
    mermaid.append("    Trader[Trader]")
    
    # Risk analysis phase
    mermaid.append("    Trader --> Risky")
    mermaid.append("    Risky[Risky Analyst]")
    mermaid.append("    Safe[Safe Analyst]")
    mermaid.append("    Neutral[Neutral Analyst]")
    mermaid.append("    Judge[Risk Judge]")
    
    mermaid.append("    Risky -->|Need Safe View?| Safe")
    mermaid.append("    Risky -->|Ready| Judge")
    mermaid.append("    Safe -->|Need Neutral?| Neutral")
    mermaid.append("    Safe -->|Ready| Judge")
    mermaid.append("    Neutral -->|Reconsider?| Risky")
    mermaid.append("    Neutral -->|Ready| Judge")
    
    # End
    mermaid.append("    Judge --> End([END])")
    
    # Styling
    mermaid.append("")
    mermaid.append("    style Start fill:#90EE90")
    mermaid.append("    style End fill:#FFB6C1")
    mermaid.append("    style Bull fill:#FFE4B5")
    mermaid.append("    style Bear fill:#FFE4B5")
    mermaid.append("    style Manager fill:#DDA0DD")
    mermaid.append("    style Trader fill:#87CEEB")
    mermaid.append("    style Risky fill:#FFA07A")
    mermaid.append("    style Safe fill:#98FB98")
    mermaid.append("    style Neutral fill:#F0E68C")
    mermaid.append("    style Judge fill:#DDA0DD")
    
    for analyst in selected_analysts:
        mermaid.append(analyst_colors[analyst].replace(analyst.capitalize(), analyst.capitalize()))
    
    diagram = "\n".join(mermaid)
    
    # Save to file
    with open("trading_graph.mmd", "w") as f:
        f.write(diagram)
    
    print("✅ Mermaid diagram saved to: trading_graph.mmd")
    print("\n" + "="*60)
    print("TRADING AGENTS WORKFLOW GRAPH")
    print("="*60)
    print(diagram)
    print("\n" + "="*60)
    print("\nTo view this diagram:")
    print("1. Copy the content above")
    print("2. Visit: https://mermaid.live")
    print("3. Paste and view the interactive diagram")
    print("\nOr install VS Code Mermaid extension to preview .mmd files")
    
    # Also create a simple text representation
    print("\n" + "="*60)
    print("TEXT REPRESENTATION")
    print("="*60)
    print("\n📊 Workflow Flow:\n")
    print("START")
    for i, analyst in enumerate(selected_analysts):
        print(f"  ↓")
        print(f"  {analyst.upper()} ANALYST")
        print(f"  ├─ Tools (if needed)")
        print(f"  └─ Clear Messages")
    print("  ↓")
    print("  BULL RESEARCHER ⟷ BEAR RESEARCHER")
    print("  ↓")
    print("  RESEARCH MANAGER")
    print("  ↓")
    print("  TRADER")
    print("  ↓")
    print("  RISKY ANALYST ⟷ SAFE ANALYST ⟷ NEUTRAL ANALYST")
    print("  ↓")
    print("  RISK JUDGE")
    print("  ↓")
    print("END")

if __name__ == "__main__":
    # Default configuration with market, social, and news analysts
    visualize_trading_graph(selected_analysts=["market", "social", "news"])
