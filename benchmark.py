import time
import requests
import sys

API_URL = "http://localhost:8001/v1/chat/completions"
HEALTH_URL = "http://localhost:8001/health"

def wait_for_server(timeout=300):
    start = time.time()
    print("⏳ Waiting for server to start...")
    while time.time() - start < timeout:
        try:
            resp = requests.get(HEALTH_URL)
            if resp.status_code == 200:
                print("✅ Server is UP!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
        sys.stdout.write(".")
        sys.stdout.flush()
    print("\n❌ Server failed to start in time.")
    return False

def benchmark_inference():
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about coding in Python."}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }

    print("\n🚀 Starting Benchmark Request...")
    start_time = time.time()
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        end_time = time.time()
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        tokens = data['usage']['completion_tokens']
        
        duration = end_time - start_time
        tps = tokens / duration

        print("-" * 40)
        print(f"📝 Response:\n{content.strip()}")
        print("-" * 40)
        print(f"⏱️  Total Duration: {duration:.2f}s")
        print(f"📊 Tokens Generated: {tokens}")
        print(f"⚡ Speed: {tps:.2f} tokens/sec")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Benchmark execution failed: {e}")

if __name__ == "__main__":
    if wait_for_server():
        benchmark_inference()
