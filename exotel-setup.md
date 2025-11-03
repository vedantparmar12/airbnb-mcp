# Exotel Setup for Indian Phone Numbers

## Step 1: Get Exotel Account
1. Sign up at: https://exotel.com/signup
2. Complete KYC (business verification - required in India)
3. Purchase a phone number (~₹500-1000/month)

## Step 2: Configure Exotel for LiveKit

1. Go to Exotel Dashboard
2. Navigate to: **Numbers** → Select your number
3. Set **Voice URL** to:
   ```
   https://airbnb-voice-agent-4ahy6tsh.livekit.cloud/sip
   ```

## Step 3: Get Exotel Credentials
- SID (Account SID)
- API Key
- API Token
- Phone Number

## Step 4: Create LiveKit Inbound Trunk

Use the LiveKit Cloud Dashboard:
1. Go to: https://cloud.livekit.io/projects/p_/telephony/config
2. Create new Inbound Trunk
3. Add your Exotel number (format: +91XXXXXXXXXX)

## Note
Exotel has specific compliance requirements for Indian telecom regulations.
