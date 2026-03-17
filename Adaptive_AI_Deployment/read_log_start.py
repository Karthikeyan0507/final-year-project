with open('d:/Adaptive_AI/Adaptive_AI_Deployment/test_log.txt', 'r', encoding='utf-16') as f:
    lines = f.readlines()
    for line in lines[:200]: # Read first 200 lines
        print(line.strip())
