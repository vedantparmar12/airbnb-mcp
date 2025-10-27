# Setup Indian Number with Twilio

## Prerequisites
- Twilio account (you have this ✓)
- Business documents for India verification (may be required)

## Step 1: Check Availability
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/search
2. Select: India (+91)
3. Check if numbers are available

## Step 2: Regulatory Requirements (If Required)
If Twilio requires regulatory bundle:
1. Go to: https://console.twilio.com/us1/develop/regulatory-compliance/bundles
2. Create new bundle
3. Upload required documents:
   - Business registration
   - Address proof
   - Identity proof
4. Wait for approval (1-3 business days)

## Step 3: Purchase Number
Once approved:
1. Search for Indian number
2. Buy number (~₹75-150/month)
3. Note the number (e.g., +91XXXXXXXXXX)

## Step 4: Update TwiML Bin
1. Go to: https://console.twilio.com/us1/develop/twiml-bins/twiml-bins
2. Edit "LiveKit Airbnb Agent"
3. Update XML with Indian number:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial>
    <Sip>sip:+91XXXXXXXXXX@airbnb-voice-agent-4ahy6tsh.sip.livekit.cloud</Sip>
  </Dial>
</Response>
```

## Step 5: Configure Phone Number
1. Click on your Indian number
2. Voice Configuration:
   - Configure with: TwiML Bin
   - A call comes in: LiveKit Airbnb Agent
   - Save

## Step 6: Update LiveKit Inbound Trunk
1. Go to: https://cloud.livekit.io/projects/p_/telephony/config
2. Edit inbound trunk
3. Update number to: +91XXXXXXXXXX
4. Save

## Step 7: Test!
Call your Indian number from any phone in India!

## Costs (Approximate)
- Number rental: ₹75-150/month
- Inbound calls: ₹0.50-1.00/min
- Very affordable for Indian users!
