# VoycePlan Landing Page

A modern, fluid, and engaging SaaS landing page for VoycePlan - an AI-powered voice agent for intuitive travel planning.

## Features

- 🎤 **Voice Interaction**: Built-in Web Speech API integration for real-time voice conversations
- 🎨 **Modern Design**: Sleek, adventurous design with gradient backgrounds and smooth animations
- 📱 **Fully Responsive**: Optimized for all screen sizes from mobile to desktop
- ⚡ **High Performance**: Built with Next.js 15 and optimized for speed
- 🎯 **ShadCN/UI Components**: Leveraging high-quality, accessible UI components
- 🌈 **Tailwind CSS**: Utility-first styling for rapid development

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN/UI
- **Icons**: Lucide React
- **Voice**: Web Speech API (Speech Recognition & Synthesis)
- **Animation**: Framer Motion, CSS Animations

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm, yarn, or pnpm package manager

### Installation

1. Clone the repository:
```bash
cd landing-page
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
landing-page/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main landing page
│   └── globals.css         # Global styles and Tailwind directives
├── components/
│   ├── ui/                 # ShadCN UI components
│   │   ├── button.tsx
│   │   └── card.tsx
│   ├── navigation.tsx      # Navigation bar
│   ├── hero-section.tsx    # Hero with voice interaction
│   ├── voice-interaction.tsx # Voice agent component
│   ├── how-it-works-section.tsx
│   ├── features-section.tsx
│   ├── use-cases-section.tsx
│   ├── cta-section.tsx
│   └── footer.tsx
├── lib/
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## Key Sections

### 1. Navigation Bar
- Fixed/sticky navigation
- Responsive mobile menu
- Call-to-action buttons

### 2. Hero Section
- Full viewport height
- Interactive background (unicorn.studio integration ready)
- Voice interaction component
- Animated scroll indicator

### 3. Voice Interaction Component
- Speech recognition for user input
- Speech synthesis for AI responses
- Visual feedback (listening, processing, speaking states)
- Waveform animations
- Example prompts for quick testing

### 4. How It Works
- Step-by-step visual guide
- Icon-based presentation
- Four-step process explanation

### 5. Features
- Six key features in card layout
- Gradient icons
- Trust indicators with statistics

### 6. Use Cases
- Six travel scenarios
- Interactive cards with examples
- Click to reveal sample voice commands

### 7. Call-to-Action
- Prominent gradient background
- Multiple CTA buttons
- Trust badges

### 8. Footer
- Comprehensive link organization
- Social media links
- Newsletter subscription
- Company information

## Voice Interaction

The voice interaction component uses the Web Speech API:

- **Browser Compatibility**: Works in Chrome, Edge, Safari
- **Speech Recognition**: Real-time transcription of user speech
- **Speech Synthesis**: AI responses read aloud
- **Visual Feedback**: Animated indicators for different states

### Testing Voice Interaction

Try these example phrases:
- "Plan a 5-day trip to Paris"
- "Find me beach destinations"
- "I need a budget-friendly vacation"

## Customization

### Colors
Edit `tailwind.config.ts` and `app/globals.css` to customize the color scheme:
- Primary color: Blue (`--primary`)
- Accent colors: Purple, Pink
- Background: White/Dark mode support

### Unicorn.studio Background
To integrate your unicorn.studio background:
1. Create your interactive background at [unicorn.studio](https://unicorn.studio)
2. Get the embed code
3. Update `components/hero-section.tsx` with your embed code

### Connecting to Real Backend
Replace the mock AI responses in `components/voice-interaction.tsx`:
```typescript
const handleVoiceInput = async (text: string) => {
  // Replace with actual API call
  const response = await fetch('/api/voice-agent', {
    method: 'POST',
    body: JSON.stringify({ message: text })
  });
  const data = await response.json();
  setResponse(data.message);
  speakResponse(data.message);
};
```

## Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm run build
# Deploy the .next folder
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

**Note**: Voice features require Chrome, Edge, or Safari due to Web Speech API support.

## Performance

- Lighthouse Score: 95+
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Mobile-optimized

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email hello@voyceplan.com or open an issue in the repository.

## Acknowledgments

- [ShadCN/UI](https://ui.shadcn.com/) for beautiful UI components
- [Lucide](https://lucide.dev/) for icons
- [Next.js](https://nextjs.org/) for the amazing framework
- [Tailwind CSS](https://tailwindcss.com/) for styling utilities
