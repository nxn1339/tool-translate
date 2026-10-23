# Release Command Matrix

Commands run from `apps/mobile` (relative to workspace root).

## Clean & Prepare

```bash
cd apps/mobile
fvm flutter clean
fvm flutter pub get
```

## Local Debug

### Android debug APK

```bash
cd apps/mobile
fvm flutter build apk --debug \
  --dart-define=API_BASE_URL=http://localhost:3000/api/v1 \
  --dart-define=ENABLE_GOOGLE_SIGN_IN=false \
  --dart-define=GOOGLE_OAUTH_CLIENT_ID=""
```

### iOS debug without signing

```bash
cd apps/mobile
fvm flutter build ios --debug --no-codesign \
  --dart-define=API_BASE_URL=http://localhost:3000/api/v1 \
  --dart-define=ENABLE_GOOGLE_SIGN_IN=false \
  --dart-define=GOOGLE_OAUTH_CLIENT_ID=""
```

### iOS debug with local signing

```bash
cd apps/mobile
fvm flutter build ios --debug \
  --dart-define=API_BASE_URL=http://localhost:3000/api/v1 \
  --dart-define=ENABLE_GOOGLE_SIGN_IN=false \
  --dart-define=GOOGLE_OAUTH_CLIENT_ID=""
```

## Production Candidate / Store Release

> 💡 **Khuyên dùng (Đọc tập trung từ file `env/env.prod.json`):**  
> Sao chép `apps/mobile/env/env.prod.json.example` thành `apps/mobile/env/env.prod.json` và điền cấu hình thực tế trước khi build.

### Android release AAB for Google Play Store (Khuyên dùng)

```bash
cd apps/mobile
fvm flutter build appbundle --release --dart-define-from-file=env/env.prod.json
```

*Hoặc truyền cờ thủ công:*

```bash
cd apps/mobile
fvm flutter build appbundle --release \
  --dart-define=API_BASE_URL=https://api.smilewishlist.com/api/v1 \
  --dart-define=ENABLE_GOOGLE_SIGN_IN=true \
  --dart-define=GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID" \
  --dart-define=ADMOB_ANDROID_INTERSTITIAL_ID="$ADMOB_ANDROID_INTERSTITIAL_ID" \
  --dart-define=ADMOB_ANDROID_REWARDED_ID="$ADMOB_ANDROID_REWARDED_ID"
```

Expected artifact:

```text
apps/mobile/build/app/outputs/bundle/release/app-release.aab
```

### Android release APK for real-device smoke test

```bash
cd apps/mobile
fvm flutter build apk --release --dart-define-from-file=env/env.prod.json
```

Expected artifact:

```text
apps/mobile/build/app/outputs/flutter-apk/app-release.apk
```

### iOS release IPA for App Store Connect / TestFlight (Khuyên dùng)

```bash
cd apps/mobile
fvm flutter build ipa --release --dart-define-from-file=env/env.prod.json
```

*Hoặc truyền cờ thủ công:*

```bash
cd apps/mobile
fvm flutter build ipa --release \
  --dart-define=API_BASE_URL=https://api.smilewishlist.com/api/v1 \
  --dart-define=ENABLE_GOOGLE_SIGN_IN=true \
  --dart-define=GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID" \
  --dart-define=ADMOB_IOS_INTERSTITIAL_ID="$ADMOB_IOS_INTERSTITIAL_ID" \
  --dart-define=ADMOB_IOS_REWARDED_ID="$ADMOB_IOS_REWARDED_ID"
```

Expected artifact:

```text
apps/mobile/build/ios/ipa/*.ipa
```

## Required Local Secret Setup

### Android Keystore

`apps/mobile/android/key.properties` is local and ignored:

```properties
storePassword=<redacted in evidence>
keyPassword=<redacted in evidence>
keyAlias=upload
storeFile=../upload-keystore.jks
```

### iOS Google Sign-In

Copy the iOS reversed client ID for bundle ID `org.smilesoftware.wishlove` to clipboard, then run:

```bash
cd apps/mobile

security add-generic-password -a "$USER" -s smile-wishlist-ios-reversed-client-id -w "$(pbpaste)" -U
GOOGLE_REVERSED_CLIENT_ID="$(security find-generic-password -a "$USER" -s smile-wishlist-ios-reversed-client-id -w)"
printf 'GOOGLE_REVERSED_CLIENT_ID=%s\n' "$GOOGLE_REVERSED_CLIENT_ID" > ios/Flutter/LocalGoogleSignIn.xcconfig
chmod 600 ios/Flutter/LocalGoogleSignIn.xcconfig
```

Do not commit `ios/Flutter/LocalGoogleSignIn.xcconfig`.
