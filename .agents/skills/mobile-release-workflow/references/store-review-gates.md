# Store Review Gates

## Google Play Gates

| Gate ID | Gate | Required Evidence |
|---|---|---|
| `REL-GOOGLE-001` | Package/application ID is `org.smilesoftware.wishlove` | Gradle config diff and build log |
| `REL-GOOGLE-002` | Release AAB is signed with upload keystore | AAB signing report or Play Console upload validation |
| `REL-GOOGLE-003` | Target SDK meets Google Play requirement on submission date | Gradle config and Play Console pre-check |
| `REL-GOOGLE-004` | Production build uses HTTPS and no release cleartext traffic | Manifest merge report and release smoke evidence |
| `REL-GOOGLE-005` | Google OAuth Android package and SHA-1/SHA-256 registered | Google Cloud OAuth screenshot or evidence note |
| `REL-GOOGLE-006` | Closed test has at least 12 opted-in testers for 14 continuous days; target list has 15-20 testers | Play Console tester evidence |
| `REL-GOOGLE-007` | Data Safety form covers account info, photos/media, user-generated content, and deletion URL | Store metadata evidence |

## Apple Gates

| Gate ID | Gate | Required Evidence |
|---|---|---|
| `REL-APPLE-001` | Bundle ID is `org.smilesoftware.wishlove` | Xcode project setting and build log |
| `REL-APPLE-002` | Automatic signing uses Apple team `962H2TSAJW` | Xcode signing evidence |
| `REL-APPLE-003` | Camera/photo permission prompts match app usage | Real-device or simulator evidence |
| `REL-APPLE-004` | iOS Google OAuth reversed client ID works for callback | Sign-in evidence on simulator or iPhone |
| `REL-APPLE-005` | IPA uploaded to TestFlight | App Store Connect/TestFlight evidence |
| `REL-APPLE-006` | Sign in with Apple works or valid exception is documented | TestFlight evidence or review note |
| `REL-APPLE-007` | Account deletion exists in app and web | API/mobile/web evidence |
| `REL-APPLE-008` | Privacy Nutrition Labels, support URL, privacy policy URL, and reviewer notes are complete | Store metadata evidence |

## Shared Gates

| Gate ID | Gate | Required Evidence |
|---|---|---|
| `REL-SHARED-001` | Backend production HTTPS `/api/v1/health` passes | Backend evidence |
| `REL-SHARED-002` | Socket.IO `/api/v1/socket.io` works through production proxy (namespace `/realtime`) | Backend realtime evidence |
| `REL-SHARED-003` | Reviewer demo accounts exist, paired, with sample wishlist data | Reviewer evidence with password owner, no password in repo |
| `REL-SHARED-004` | Store screenshots and descriptions accurately showcase Phase 1 features (Love Diary, Love Tree, Wishlist, Couple Home) | Store listing review evidence |
| `REL-SHARED-005` | PM, QA, and Tech Lead approval recorded before public submission | Checklist approval table |
| `REL-SHARED-006` | Google Mobile Ads (AdMob) app-ads.txt on domain and production Ad Unit IDs verified | Domain app-ads.txt verification and build config |

