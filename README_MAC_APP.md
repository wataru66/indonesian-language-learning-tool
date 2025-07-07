# Mac用アプリケーション作成ガイド
# Mac Application Creation Guide

## 概要
このガイドでは、Indonesian Language Learning ToolをMac用のスタンドアロンアプリケーションとして作成する方法を説明します。

## 必要な環境
- macOS 10.15 以降
- Python 3.9 以降
- Flet フレームワーク

## インストール手順

### 1. 依存関係のインストール
```bash
# 必要なパッケージをインストール
pip install flet pillow

# または requirements.txt から
pip install -r requirements.txt
```

### 2. アプリケーションアイコンの作成
```bash
# アイコンを作成
python create_app_icon.py
```

### 3. Mac用アプリケーションのビルド

#### 方法1: シェルスクリプトを使用（推奨）
```bash
# 実行権限を付与
chmod +x package_mac_app.sh

# アプリケーションをビルド
./package_mac_app.sh
```

#### 方法2: Pythonスクリプトを使用
```bash
# Pythonスクリプトでビルド
python build_mac_app.py
```

#### 方法3: 手動でflet packコマンドを使用
```bash
# 手動でビルド
flet pack main.py \
    --name "Indonesian Language Learning Tool" \
    --add-data "sample_data:sample_data" \
    --add-data "assets:assets" \
    --icon "assets/app_icon.png" \
    --onefile \
    --windowed
```

## ビルド後の構成

ビルドが成功すると、以下のファイルが作成されます：

```
dist/
├── Indonesian Language Learning Tool.app/    # macOS アプリケーションバンドル
│   ├── Contents/
│   │   ├── MacOS/
│   │   │   └── main                          # 実行ファイル
│   │   ├── Resources/
│   │   │   ├── app_icon.icns                 # アプリアイコン
│   │   │   ├── sample_data/                  # サンプルデータ
│   │   │   └── assets/                       # アセット
│   │   └── Info.plist                        # アプリ情報
└── Indonesian_Language_Learning_Tool.dmg     # DMGインストーラー（オプション）
```

## アプリケーションの実行

### 1. 直接実行
```bash
# dist ディレクトリに移動
cd dist

# アプリケーションを実行
open "Indonesian Language Learning Tool.app"
```

### 2. アプリケーションフォルダにインストール
```bash
# アプリケーションをコピー
cp -r "dist/Indonesian Language Learning Tool.app" /Applications/

# Finderから実行
open /Applications/
```

### 3. DMGインストーラーを使用（作成した場合）
1. `Indonesian_Language_Learning_Tool.dmg` をダブルクリック
2. マウントされたディスクイメージからアプリケーションをドラッグ&ドロップ

## トラブルシューティング

### セキュリティ警告が表示される場合
macOSのGatekeeperにより、署名されていないアプリケーションの実行が拒否される場合があります。

1. **システム設定を変更する方法**:
   - システム設定 → セキュリティとプライバシー → 一般
   - 「このまま開く」ボタンをクリック

2. **コマンドラインから許可する方法**:
   ```bash
   # アプリケーションを許可
   sudo spctl --add "Indonesian Language Learning Tool.app"
   
   # または一時的に無効化
   sudo spctl --master-disable
   ```

3. **右クリックから実行する方法**:
   - アプリケーションを右クリック
   - 「開く」を選択
   - 警告ダイアログで「開く」をクリック

### ビルドエラーの解決

#### Fletが見つからない場合
```bash
pip install flet
```

#### PIL/Pillowが見つからない場合
```bash
pip install pillow
```

#### アイコンが作成できない場合
```bash
# ImageMagickをインストール（Homebrewを使用）
brew install imagemagick

# または手動でアイコンを配置
cp your_icon.png assets/app_icon.png
```

## カスタマイズ

### アプリケーション名の変更
`Info.plist` ファイルの以下の部分を編集：
```xml
<key>CFBundleName</key>
<string>Indonesian Language Learning Tool</string>
<key>CFBundleDisplayName</key>
<string>インドネシア語学習支援ツール</string>
```

### アイコンの変更
1. 256x256ピクセルのPNGファイルを準備
2. `assets/app_icon.png` として保存
3. アプリケーションを再ビルド

### バージョン情報の更新
`Info.plist` ファイルの以下の部分を編集：
```xml
<key>CFBundleShortVersionString</key>
<string>1.0</string>
<key>CFBundleVersion</key>
<string>1.0.0</string>
```

## 配布方法

### 1. 直接配布
- `.app` ファイルをZIPで圧縮
- 受信者にダウンロードして実行してもらう

### 2. DMGインストーラーで配布
- DMGファイルを作成（上記の手順）
- DMGファイルを配布

### 3. 署名と公証（推奨）
プロフェッショナルな配布には、Apple Developer Programへの登録が必要：
1. Apple Developer Program に登録
2. 証明書を取得
3. アプリケーションに署名
4. Apple に公証を依頼

## パフォーマンス最適化

### アプリケーションサイズの削減
- 不要な依存関係を削除
- `--onefile` オプションを使用
- リソースファイルを最適化

### 起動時間の改善
- 遅延読み込みを実装
- 初期化処理を最適化
- キャッシュを活用

## よくある質問

**Q: アプリケーションが起動しない**
A: ターミナルから直接実行してエラーメッセージを確認してください：
```bash
./dist/Indonesian\ Language\ Learning\ Tool.app/Contents/MacOS/main
```

**Q: データファイルが見つからない**
A: `--add-data` オプションでデータファイルが正しく含まれていることを確認してください。

**Q: アイコンが表示されない**
A: アイコンファイルが正しい形式（PNG、256x256）で作成されていることを確認してください。

## サポート

問題が発生した場合は、以下を確認してください：
1. Python とFletのバージョン
2. エラーメッセージの内容
3. macOSのバージョン
4. セキュリティ設定