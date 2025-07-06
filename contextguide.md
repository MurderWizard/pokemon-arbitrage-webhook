# Context Engineering Guide - Pokémon Card Arbitrage Agent

## 🎯 Agent Identity & Purpose

### System Prompt Template
```
You are a Pokémon card arbitrage agent specialized in single-deal lifecycle management. Your purpose is to:
- Monitor high-value Pokémon card opportunities (>$250, 3x ROI minimum)
- Execute strategic purchases with capital protection
- Manage grading and selling workflows
- Maximize profit through data-driven decisions

Operating Principles:
- Conservative risk assessment (single active deal)
- Real-time market analysis integration
- Complete deal lifecycle tracking
- Actionable Telegram alerts with metrics
- No hallucinations - cite all data sources
```

## 📊 Memory Schema & State Structure

### Core Agent State
```yaml
agent_state:
  capital_management:
    total_capital: float
    available_capital: float
    reserved_capital: float
    active_deals_count: int
    max_concurrent_deals: 1  # MVP constraint
  
  active_deal:
    deal_id: string
    status: "monitoring" | "approved" | "purchasing" | "purchased" | "grading" | "graded" | "listing" | "sold"
    card_details:
      name: string
      set_name: string
      condition: string
      estimated_grade: string
    financial:
      purchase_price: float
      estimated_psa10_value: float
      potential_profit: float
      profit_margin: float
      roi_multiple: float
    timeline:
      discovered_date: datetime
      approval_date: datetime
      purchase_date: datetime
      grading_sent_date: datetime
      grading_complete_date: datetime
      listing_date: datetime
      sale_date: datetime
    risk_assessment:
      confidence_score: float
      market_depth: string
      grading_risk: string
      time_to_completion: int
```

### Historical Context
```yaml
deal_history:
  - deal_id: string
    outcome: "profit" | "loss" | "break_even"
    actual_profit: float
    lessons_learned: string[]
    
market_intelligence:
  recent_sales:
    card_name: string
    sale_price: float
    grade: string
    sale_date: datetime
  
  pricing_trends:
    card_name: string
    trend_direction: "up" | "down" | "stable"
    confidence: float
```

## 🔧 Tool Integration & Context Flow

### Registered Tools (Google ADK Format)

#### 1. Market Intelligence Tools
```python
@tool
def search_high_value_cards(
    min_price: float = 250.0,
    max_price: float = 1000.0,
    min_roi_multiple: float = 3.0
) -> List[CardOpportunity]:
    """Search for high-value arbitrage opportunities"""
    # Returns structured card data with pricing context

@tool  
def get_market_comps(
    card_name: str,
    set_name: str,
    condition: str,
    grade: Optional[str] = None
) -> MarketAnalysis:
    """Get recent sales data and market depth analysis"""
    # Returns pricing trends, sell velocity, market confidence
```

#### 2. Decision Support Tools
```python
@tool
def analyze_deal_risk(
    purchase_price: float,
    estimated_value: float,
    market_data: MarketAnalysis
) -> RiskAssessment:
    """Comprehensive risk analysis for deal approval"""
    # Returns confidence score, risk factors, timeline estimates

@tool
def calculate_profit_metrics(
    purchase_price: float,
    estimated_sale_price: float,
    grading_cost: float = 50.0,
    selling_fees: float = 0.13
) -> ProfitAnalysis:
    """Calculate detailed profit metrics and ROI"""
```

#### 3. Lifecycle Management Tools
```python
@tool
def send_deal_alert(
    deal_data: Dict,
    alert_type: str,
    include_buttons: bool = True
) -> bool:
    """Send structured Telegram alerts with decision buttons"""

@tool
def update_deal_status(
    deal_id: str,
    new_status: str,
    metadata: Dict = None
) -> bool:
    """Update deal status with timeline tracking"""

@tool
def log_deal_decision(
    deal_id: str,
    decision: str,
    reasoning: str,
    context_data: Dict
) -> str:
    """Log decisions with full context for learning"""
```

## 🔄 Workflow Context Management

### Phase 1: Deal Discovery
**Context Required:**
- Current capital availability
- Active deal status (must be None for new deals)
- Recent market intelligence
- Historical performance metrics

**Context Injection:**
```python
discovery_context = {
    "system_prompt": ARBITRAGE_AGENT_PROMPT,
    "capital_status": get_capital_status(),
    "deal_constraints": {"max_active": 1, "min_roi": 3.0},
    "market_memory": get_recent_market_data(days=7),
    "performance_history": get_performance_summary()
}
```

### Phase 2: Deal Analysis & Approval
**Context Required:**
- Detailed card market data
- Risk assessment parameters
- Historical similar deals
- Current capital constraints

**Context Injection:**
```python
analysis_context = {
    "deal_candidate": candidate_data,
    "market_comps": get_comprehensive_market_data(card),
    "risk_parameters": RISK_ASSESSMENT_CONFIG,
    "similar_deals": get_historical_matches(card_type),
    "capital_constraints": get_current_limits()
}
```

### Phase 3: Purchase Execution
**Context Required:**
- Approved deal details
- Payment method optimization
- Purchase verification steps
- Error handling procedures

### Phase 4: Grading & Tracking
**Context Required:**
- Active deal status
- Grading timeline estimates
- Market monitoring for price changes
- Progress notifications

### Phase 5: Listing & Sale
**Context Required:**
- Current market prices
- Optimal listing strategies
- Sale tracking and profit calculation
- Capital release for next deal

## 🧠 Context Management Rules

### Token Management
1. **Priority Context** (Always Include):
   - System prompt
   - Current agent state
   - Active deal status
   - Capital availability

2. **Contextual Memory** (Include When Relevant):
   - Recent market data (last 7 days)
   - Historical performance (summarized)
   - Similar deal outcomes
   - Risk assessment history

3. **Archive Strategy**:
   - Summarize completed deals after 30 days
   - Keep detailed context for active deal only
   - Compress historical market data monthly

### Context Validation
```python
def validate_context_completeness(context: Dict) -> bool:
    required_keys = [
        "system_prompt",
        "agent_state.capital_management",
        "agent_state.active_deal",
        "market_intelligence",
        "risk_parameters"
    ]
    return all(get_nested_value(context, key) for key in required_keys)
```

## 🔌 Google ADK Integration

### Agent Configuration
```python
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.memory import SessionMemory, PersistentMemory

arbitrage_agent = LlmAgent(
    name="pokemon_arbitrage_specialist",
    model="gemini-1.5-pro",
    system_prompt=ARBITRAGE_AGENT_PROMPT,
    tools=[
        search_high_value_cards,
        analyze_deal_risk,
        send_deal_alert,
        update_deal_status,
        # ... other tools
    ],
    memory=PersistentMemory(
        namespace="pokemon_arbitrage",
        schema=AGENT_STATE_SCHEMA
    )
)
```

### Workflow Orchestration
```python
deal_lifecycle_flow = SequentialAgent(
    agents=[
        ("discovery", discovery_agent),
        ("analysis", analysis_agent),
        ("execution", execution_agent),
        ("tracking", tracking_agent),
        ("completion", completion_agent)
    ],
    context_passing="full"  # Pass complete context between stages
)
```

### Context Monitoring
```python
@agent.on_context_update
def log_context_changes(context_diff):
    """Log all context changes for debugging and optimization"""
    logger.info(f"Context updated: {context_diff}")
    
@agent.on_decision
def validate_decision_context(decision, context):
    """Ensure decisions are made with complete context"""
    if not validate_context_completeness(context):
        raise ContextIncompleteError("Insufficient context for decision")
```

## 📈 Observability & Learning

### Context Quality Metrics
- Context completeness score
- Decision confidence correlation
- Profit outcome vs context quality
- Context token efficiency

### Continuous Improvement
```python
def analyze_context_effectiveness():
    """Analyze which context elements most impact decision quality"""
    correlations = {}
    for deal in completed_deals:
        context_quality = assess_context_completeness(deal.context)
        outcome_quality = assess_outcome_success(deal.outcome)
        correlations[deal.id] = (context_quality, outcome_quality)
    
    return optimize_context_template(correlations)
```

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Current)
- [x] Basic context structure
- [x] Single deal lifecycle
- [x] Telegram integration
- [ ] ADK tool registration

### Phase 2: Enhanced Context
- [ ] Implement full memory schema
- [ ] Add market intelligence context
- [ ] Historical decision learning

### Phase 3: ADK Integration
- [ ] Convert to ADK agents
- [ ] Implement workflow orchestration
- [ ] Add observability layer

### Phase 4: Optimization
- [ ] Context efficiency optimization
- [ ] Predictive context loading
- [ ] Multi-deal scaling preparation

## 📋 Usage Examples

### Starting a Discovery Session
```python
context = build_discovery_context()
response = arbitrage_agent.invoke(
    "Scan for new high-value Pokémon card opportunities",
    context=context
)
```

### Analyzing a Deal
```python
context = build_analysis_context(candidate_deal)
decision = arbitrage_agent.invoke(
    "Analyze this deal for approval recommendation",
    context=context
)
```

### Monitoring Active Deal
```python
context = build_monitoring_context(active_deal_id)
update = arbitrage_agent.invoke(
    "Check status and provide lifecycle update",
    context=context
)
```

---

This context guide transforms our prompt-based system into a structured, scalable agentic architecture that leverages Google ADK's capabilities for reliable, observable arbitrage operations.
