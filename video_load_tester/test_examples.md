# 🧪 Load Tester Testing Examples

## 📋 Test URLs to Try

### **Facebook Games (Real Examples)**
```
https://www.facebook.com/games
https://www.facebook.com/games/farmville
https://apps.facebook.com/candycrushsaga/
https://www.facebook.com/games/wordswithfriends
```

### **Popular Web Games**
```
https://agar.io
https://slither.io
https://krunker.io
https://diep.io
```

### **General Websites**
```
https://httpbin.org (Great for API testing)
https://jsonplaceholder.typicode.com
https://reqres.in
https://httpstat.us
```

### **Your Local Test Server**
```
http://localhost:3000 (Our game API simulator)
```

## 🎯 Testing Steps

### **1. Basic Functionality Test**
1. Open http://localhost:5001
2. Enter URL: `http://localhost:3000`
3. Click "Analyze Website"
4. Should create scenarios automatically
5. Select a scenario and run with 5 users for 60 seconds

### **2. Facebook Game Test**
1. Enter URL: `https://www.facebook.com/games`
2. Click "Analyze Website"
3. Should detect it as Facebook game
4. Should create Facebook-specific scenarios
5. Run test with 10 users for 120 seconds

### **3. Web Game Test**
1. Enter URL: `https://agar.io`
2. Click "Analyze Website"
3. Should create generic web scenarios
4. Run test and monitor metrics

### **4. API Testing Site**
1. Enter URL: `https://httpbin.org`
2. Click "Analyze Website"
3. Should create API-focused scenarios
4. Perfect for testing HTTP methods

## 📊 What to Look For

### **✅ Success Indicators**
- Website analysis completes without errors
- Scenarios are generated automatically
- Load test starts and shows "RUNNING" status
- Real-time metrics update every 5 seconds
- Successful requests > 80%
- Response times < 5 seconds

### **⚠️ Warning Signs**
- Analysis fails (network issues)
- All requests fail (URL not accessible)
- Very high response times (>10 seconds)
- High error rates (>20% failures)

### **❌ Error Scenarios**
- Invalid URLs
- Sites that block automated requests
- Rate-limited APIs
- Authentication-required sites

## 🔧 Troubleshooting

### **If Analysis Fails**
```bash
# Check if the tester is running
curl http://localhost:5001

# Test with a simple URL
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:3000"}'
```

### **If Load Test Fails**
- Start with fewer users (5-10)
- Use shorter duration (60-120 seconds)
- Test with local simulator first
- Check target website accessibility

## 🎮 Advanced Testing

### **Test Your Own Game**
1. Replace `http://localhost:3000` with your game URL
2. Make sure your game APIs are accessible
3. Start with low load (10 users)
4. Gradually increase load
5. Monitor your server performance

### **Test Production Sites**
⚠️ **Important**: Only test sites you own or have permission to test
- Start with very low load (1-5 users)
- Respect rate limits
- Monitor for blocking/banning
- Use realistic user behavior

## 📈 Interpreting Results

### **Good Performance**
- Success rate: >95%
- Response time: <2 seconds
- No timeout errors
- Consistent performance

### **Needs Optimization**
- Success rate: 80-95%
- Response time: 2-5 seconds
- Occasional timeouts
- Performance degrades over time

### **Poor Performance**
- Success rate: <80%
- Response time: >5 seconds
- Frequent errors
- Server overload indicators
