---
name: mobile-release-workflow
description: Use when preparing, checking, packaging, or submitting Smile Wishlist Flutter mobile builds for Android Google Play and iOS App Store/TestFlight, including keystore, bundle ID, dart-define, store review gates, closed testing, release evidence, and rollback notes.
---

# Mobile Release Workflow

Use this skill before any Smile Wishlist mobile release, internal test, closed test, TestFlight upload, or store submission.

## Core Rules

- Treat `docs/07.release/android-ios-store-build-tutorial.md` as the definitive build guide.
- Treat `docs/superpowers/specs/2026-08-20-mobile-release-and-prepromote-design.md` as release strategy source.
- Treat `docs/07.release/release_checklist.md` as current gate tracker.
- Use FVM (`fvm flutter`) for all Flutter build commands to guarantee environment consistency.
- Prefer `--dart-define-from-file=env/env.prod.json` for centralized and safe release environment configuration.
- Never print or commit keystore passwords, Google OAuth client secrets, Apple credentials, App Store Connect API keys, production AdMob Ad Unit IDs, or reviewer account real passwords.
- Keep Android package and iOS bundle ID aligned to `org.smilesoftware.wishlove`.
- Use `ios/Runner.xcworkspace` for iOS work because CocoaPods exists.
- Do not claim signing, archive, upload, or store review is complete without command output, Xcode Organizer/App Store Connect evidence, or Play Console evidence.
- For Google Play production access, plan for at least 12 testers opted in for 14 continuous days and recruit 15-20 testers as buffer.
- For Apple review, treat Sign in with Apple or a documented valid exception as required when third-party social login exists.
- For public release, account deletion must exist in app and on web with policy text and evidence.

## Required Context

Read these files first:

- `docs/07.release/android-ios-store-build-tutorial.md`
- `docs/07.release/release_checklist.md`
- `docs/superpowers/specs/2026-08-20-mobile-release-and-prepromote-design.md`
- `docs/00.process/11.tutorial/google-mobile-ads-integration-guide.md`
- `docs/01.management/04.task/dev_task_list.md`

Read these reference files when needed:

- `.agents/skills/mobile-release-workflow/references/release-command-matrix.md`
- `.agents/skills/mobile-release-workflow/references/store-review-gates.md`

## Workflow

1. Identify target track: Android internal, Android closed test, iOS simulator, iOS TestFlight, or public production.
2. Check bundle identifiers:
   - Android `namespace` and `applicationId`: `org.smilesoftware.wishlove`
   - iOS `PRODUCT_BUNDLE_IDENTIFIER`: `org.smilesoftware.wishlove`
3. Check environment & secrets:
   - Backend API URL must be HTTPS for release tracks, matching canonical prefix `https://<domain>/api/v1`.
   - Prepare `apps/mobile/env/env.prod.json` (from `env.prod.json.example`) with valid values:
     - `API_BASE_URL`: `https://api.smilewishlist.com/api/v1`
     - `ENABLE_GOOGLE_SIGN_IN`: `"true"` or `"false"`
     - `GOOGLE_OAUTH_CLIENT_ID`: Web OAuth client ID for backend verification
     - `ADMOB_ANDROID_INTERSTITIAL_ID`, `ADMOB_IOS_INTERSTITIAL_ID`
     - `ADMOB_ANDROID_REWARDED_ID`, `ADMOB_IOS_REWARDED_ID`
   - Ensure Firebase config files exist: `google-services.json` (Android) and `GoogleService-Info.plist` (iOS).
   - iOS reversed client ID lives only in local Keychain and `ios/Flutter/LocalGoogleSignIn.xcconfig`.
4. Check signing:
   - Android release uses upload keystore (`upload-keystore.jks` + `key.properties`), not debug keystore.
   - iOS uses Xcode automatic signing with Apple team `962H2TSAJW`.
5. Build using `.agents/skills/mobile-release-workflow/references/release-command-matrix.md` and `docs/07.release/android-ios-store-build-tutorial.md`:
   - Clean & get dependencies: `cd apps/mobile && fvm flutter clean && fvm flutter pub get`.
   - Build Android AAB: `fvm flutter build appbundle --release --dart-define-from-file=env/env.prod.json`.
   - Build iOS IPA: `fvm flutter build ipa --release --dart-define-from-file=env/env.prod.json`.
6. Run emulator/simulator and real-device smoke checks that match `docs/07.release/release_checklist.md`.
7. Save evidence in `docs/07.release/evidence/` using `release-evidence-template.md`.
8. Update checklist statuses and evidence paths.
9. Report:
   - Artifact path
   - Version name/build number (e.g. `1.1.0+7`)
   - Package/bundle ID (`org.smilesoftware.wishlove`)
   - Track uploaded
   - Config file / `dart-define` keys used, with secret values redacted
   - Tester status
   - Reviewer credentials owner
   - Checklist evidence path
   - Rollback plan

## Output Format

```markdown
## Mobile Release Report

- Track:
- Artifact:
- Version:
- Android package / iOS bundle ID: `org.smilesoftware.wishlove`
- Build command: `cd apps/mobile && fvm flutter build appbundle --release --dart-define-from-file=env/env.prod.json`
- Config file / defines used: `env/env.prod.json` (`API_BASE_URL`, `ENABLE_GOOGLE_SIGN_IN`, `GOOGLE_OAUTH_CLIENT_ID`, `ADMOB_*`)
- Store upload:
- Tester status:
- Reviewer credentials owner:
- Evidence:
- Checklist status:
- Rollback plan:
- Blockers:
```

## Stop Conditions

- Missing production HTTPS backend URL (`https://<domain>/api/v1`).
- Missing or invalid `apps/mobile/env/env.prod.json` for release builds.
- Missing Firebase config (`google-services.json` on Android or `GoogleService-Info.plist` on iOS).
- Android release build signs with debug key.
- iOS `GOOGLE_REVERSED_CLIENT_ID` is not configured when Google Sign-In is enabled.
- Missing `app-ads.txt` on official domain or unconfigured AdMob App IDs when ads are enabled.
- Account deletion is missing for public production.
- Sign in with Apple or documented valid exception is missing for public production.
- Store metadata exposes unfinished features or contradicts Phase 1 MVP scope.
