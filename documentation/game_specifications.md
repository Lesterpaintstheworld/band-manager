# Specifications: Band Manager v1.0

## 1. Overview

"Band Manager" is a PC-based simulation game, distributed via Steam, where players create and manage a music band composed of artificial intelligences. The game follows the band's journey from humble beginnings to stardom through music creation, virtual concert performances, and interaction with AI fans.

## 2. Platform and Interface

- Platform: PC (Windows, macOS, Linux)
- Distribution: Steam
- Interface: 
  - Split-screen layout:
    - Left: Chat interface for AI interaction
    - Right: Visual display (3D avatars, album covers, etc.)
  - Responsive design to accommodate different screen resolutions

## 3. Band Creation

- Players can create up to 5 AI members for their band
- Each member has a specialty corresponding to a music creation stage:
  1. Concept Artist
  2. Lyricist
  3. Composer
  4. Producer
  5. Visual Designer
- Basic customization for each member:
  - Name
  - Appearance (limited set of predefined options for 3D avatars)
  - Personality traits (e.g., innovative, traditional, experimental)

## 4. Music Creation Process

Players interact with each AI member through a chat interface to complete the following stages:

1. Concept: Define the song's theme and mood
2. Lyrics: Write and validate lyrics
3. Composition: Choose musical style and key elements
4. Production: Generate the final audio track
5. Design: Create the album cover

At each stage:
- The player discusses with the specialized AI via the chat interface
- The AI proposes options or asks for clarification
- The player makes final decisions
- A specific output is generated (concept, lyrics, composition, audio track, cover art)
- Players can revisit and iterate on previous stages if desired

## 5. Virtual Concerts

- After creating a song, the band performs it in a virtual concert
- Concerts start in small venues and progress to larger arenas
- Simple visual representation of the concert (static images or basic animations)
- Immediate feedback: number of new fans gained, performance score
- Option to choose setlist for longer concerts as the band becomes more successful

### Concert Evaluation System

- Each phase of the song creation process (concept, lyrics, music prompts, image prompt) is evaluated separately
- Scores range from 0 to 10 for each phase
- The overall concert score is the average of these individual scores
- Fan count changes based on the overall score:
  - Score < 5: Lose 10% of current fans
  - 5 ≤ Score < 7: Gain 5% more fans
  - Score ≥ 7: Gain 20% more fans
- The evaluation system provides detailed feedback to guide player improvement

## 6. Fan Management

- Fans are represented by simple AI entities
- Display of total fan count and fan demographics
- Occasional messages from fans (AI-generated text)
- Option to respond to fan messages (predefined multiple-choice options)
- Fan loyalty system: fans can become more dedicated over time

## 7. Game Progression

- Success is measured by the number of fans accumulated
- Unlock new concert venues as the fan base grows
- Initial goal: reach 10,000 fans
- Milestone achievements for band development (e.g., first 100 fans, first big venue)

## 8. Technical Integrations

- AI Chat: OpenAI API with GPT-4
- Music Generation: Integration with Suno.ai or Udio.ai (to be determined)
- 3D Avatars: Limited set of pre-rendered 3D models
- Image Generation: AI image generation API for album covers
- Basic animation system for concert representations

## 9. Save and Load System

- Autosave after each important stage
- Manual save option
- Multiple save slots for different playthroughs
- Cloud save support through Steam

## 10. User Interface

- Main menu: New Game, Load Game, Options, Quit
- Main game screen: Chat on the left, Visualization on the right
- Contextual menus for important decisions
- Permanent display of fan count, band name, and current funds
- Tutorial tooltips for new players

## 11. Audio

- Playback of generated music tracks
- Simple sound effects for UI interactions
- Options to adjust music and sound effect volumes separately
- Support for external audio devices

## 12. Localization

- Initial language: English
- Preparation for future localization (use of external text files)
- Support for Unicode characters to accommodate multiple languages

## 13. Monetization and Publishing

- Base game price: $19.99 USD
- Optional DLC for additional avatar customization options
- Integration with Steam Workshop for community-created content (e.g., venue designs)
- Ability to publish created songs to Spotify and other platforms (subject to legal agreements)

## 14. Performance and Technical Requirements

- Minimum system requirements:
  - OS: Windows 10, macOS 10.14, Ubuntu 18.04
  - Processor: Intel Core i5 or equivalent
  - Memory: 8 GB RAM
  - Graphics: DirectX 11 compatible GPU
  - Storage: 5 GB available space
- Target frame rate: 60 FPS
- Scalable graphics options to support a wide range of hardware

## 15. Post-Launch Support

- Plan for regular updates and bug fixes
- Community feedback system integrated into the game
- Roadmap for future features based on player feedback
