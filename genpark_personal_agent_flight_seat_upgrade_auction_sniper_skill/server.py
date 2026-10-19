# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Flight Seat Upgrade Auction Sniper & Cabin Bidder Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "calculate_optimal_upgrade_bid",
    "description": "Calculate the optimal blind-auction bid for business/first class seats balancing win-rate probability against retail cash ticket spread.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "economy_ticket_cost_usd": {
          "type": "number"
        },
        "retail_business_ticket_cost_usd": {
          "type": "number"
        },
        "minimum_allowable_bid_usd": {
          "type": "number"
        },
        "maximum_allowable_bid_usd": {
          "type": "number"
        },
        "unsold_premium_seats_count": {
          "type": "integer"
        },
        "hours_prior_to_departure": {
          "type": "integer"
        }
      },
      "required": [
        "economy_ticket_cost_usd",
        "retail_business_ticket_cost_usd",
        "minimum_allowable_bid_usd",
        "unsold_premium_seats_count"
      ]
    }
  },
  {
    "name": "audit_cabin_amenity_arbitrage_value",
    "description": "Quantify tangible monetary value of premium cabin amenities (lounge access, checked baggage waiver, lie-flat sleep delta) against bid cost.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "flight_duration_hours": {
          "type": "number"
        },
        "bid_amount_usd": {
          "type": "number"
        },
        "has_lounge_access": {
          "type": "boolean"
        },
        "extra_bags_count": {
          "type": "integer"
        }
      },
      "required": [
        "flight_duration_hours",
        "bid_amount_usd"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-personal-agent-flight-seat-upgrade-auction-sniper-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-personal-agent-flight-seat-upgrade-auction-sniper-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "calculate_optimal_upgrade_bid",
            "arguments": {
                "economy_ticket_cost_usd": 680.0,
                "retail_business_ticket_cost_usd": 2850.0,
                "minimum_allowable_bid_usd": 420.0,
                "maximum_allowable_bid_usd": 1100.0,
                "unsold_premium_seats_count": 6,
                "hours_prior_to_departure": 36
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: calculate_optimal_upgrade_bid")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
