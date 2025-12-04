curl -s -X POST http://localhost:8001/review -H "Content-Type: application/json" -d "{\"code\":\"$(cat $1)\"}" | jq ".overall_score"
