import sys
sys.path.insert(0, ".")
import asyncio
import pytest
from app.agents import AGENTS

@pytest.mark.asyncio
async def test_all_agents():
    for name, agent in AGENTS.items():
        try:
            result = await agent.run(context={})
            assert isinstance(result, dict)
            print(f"✓ {name}: {list(result.keys())[:3]}")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            raise

@pytest.mark.asyncio
async def test_orchestrator_cycle():
    from app.core.orchestrator import orchestrator
    from app.agents import register_all
    register_all(orchestrator)
    result = await orchestrator.run_cycle()
    assert "cycle" in result
    assert "phase" in result
    print(f"✓ orchestrator cycle {result['cycle']} phase {result['phase']}")

if __name__ == "__main__":
    asyncio.run(test_all_agents())
    asyncio.run(test_orchestrator_cycle())
    print("✅ test_agents passed")
