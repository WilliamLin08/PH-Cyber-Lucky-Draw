# Cyber Lucky Draw for Christmas 2024
## Introduction
This is a Christmas lucky draw for 2024, including 5-yuan pool and 20-yuan pool and I pool contain both 5-yuan-pool and 20-yuan-pool.

## How to use
First, choose which pool you want to use. Then, download the pool.

Second, change the probability in the code. The sum of all the probability should be 1.0. 
The code you need to change is between line 18 and 36 in overall.py, 21 and 29 between 20.py, 19 and 27 in 5.py.
        
        self.prizes_5 = {
            "🎁 Special Prize (100 RMB)":  ,
            "🎄 First Prize (50 RMB)":  ,
            "🎅 Second Prize (20 RMB)":  ,
            "❄️ Third Prize (10 RMB)":  ,
            "☃️ Fourth Prize (0 RMB)":  ,  # Renamed from "colo"
            "🎉 Try Again": 0.10,
            "🔔 No Prize": 0.528
        }

        # 20-yuan Pool - Updated as per user request
        self.prizes_20 = {
            "🎁 Special Prize (500 RMB)":  ,
            "🎄 First Prize (200 RMB)":  ,
            "🎅 Second Prize (50 RMB)":  ,
            "❄️ Third Prize (30 RMB)":  ,
            "☃️ Fourth Prize (Coke 2 RMB)":  ,
            "🎉 Try Again":  ,
            "🔔 No Prize":  
        }

# The probability used in PH Christmas Cyber lucky draw
### All probability are donated to charity

### 5-yuan-pool:

| prize     |   prob |   cost |
|:----------|-------:|-------:|
| 100       |  0.007 |  0.7   |
| 50        |  0.01  |  0.5   |
| 20        |  0.03  |  0.6   |
| 10        |  0.12  |  1.2   |
| 可乐/零食 |  0.27  |  0.54  |
| re        |  0.15  |  0.531 |
| /         |  0.413 |  0     |
| overall   |  1     |  4.071 |


### 20-yuan-pool:

| prize     |   prob |    cost |
|:----------|-------:|--------:|
| 500       |  0.007 |  3.5    |
| 200       |  0.019 |  3.8    |
| 50        |  0.051 |  2.55   |
| 30        |  0.12  |  3.6    |
| 可乐/零食 |  0.25  |  0.5    |
| re        |  0.15  |  2.0925 |
| /         |  0.403 |  0      |
| overall   |  1     | 16.0425 |


