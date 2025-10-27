# Telnyx Setup for Indian Phone Numbers

## Pricing (Very Affordable!)
- Phone number: ~₹40-80/month
- Inbound calls: ~₹0.30/min
- Outbound calls: ~₹0.40/min

## Step 1: Create Telnyx Account
1. Sign up: https://telnyx.com/sign-up
2. Verify your account
3. Add payment method

## Step 2: Purchase Indian Number
1. Go to: https://portal.telnyx.com/#/numbers/buy-numbers
2. Search for: Country = India (+91)
3. Buy a number

## Step 3: Create FQDN Connection
1. Go to: https://portal.telnyx.com/#/connections
2. Click "Create Connection"
3. Select "FQDN" type
4. Name: "LiveKit Airbnb Agent"
5. Add FQDN: `airbnb-voice-agent-4ahy6tsh.sip.livekit.cloud`
6. Save

## Step 4: Assign Number to Connection
1. Go to your purchased number
2. Connection: Select "LiveKit Airbnb Agent"
3. Save

## Step 5: Update LiveKit Inbound Trunk
1. Go to: https://cloud.livekit.io/projects/p_/telephony/config
2. Edit inbound trunk
3. Add your Telnyx Indian number: +91XXXXXXXXXX
4. Save

## Advantages
- ✅ Cheaper than Twilio
- ✅ HD Voice quality
- ✅ Better for high-volume calls
- ✅ Good Indian telecom network coverage
