#!/usr/bin/env python3
"""Sora2 ワンショット生成ツール（合成なし・一発完成）

特徴:
- 1コマンドで完成動画を生成（分割・合成・外部TTSなし）
- 強力なプリセットプロンプト（anime_op / doc_trailer）
- アスペクト比・尺・音声（ナレーション+BGM）の有無を指定可能

使い方:
  python src_sora/one_shot.py --preset anime_op \
      --title "怪物に出会った日" \
      --aspect 9:16 --duration 25 \
      --voice narration \
      --out data/procecced/videos_sora/怪物に出会った日/one_shot_anime_op.mp4

  python src_sora/one_shot.py --preset doc_trailer \
      --title "怪物に出会った日" \
      --aspect 16:9 --duration 35 \
      --voice narration

備考:
- 実在人物の顔/肖像の再現は避け、抽象・汎用の表現に寄せています。
- Soraの実出力尺は数百msの誤差が出る可能性があります。
"""

from __future__ import annotations

import argparse
from pathlib import Path
from openai import OpenAI

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


GLOBAL_STYLE = (
    "Cinematic, high quality, professional. "
    "Slow, deliberate camera moves; no jitter, no fast zooms, no jump cuts. "
    "Clean subject silhouette, gentle filmic contrast, subtle grain. "
    "Crisp motion, minimal motion blur."
)


def build_prompt_anime_op(
    title: str, duration: int, aspect: str, voice: str | None, strict: bool = False
) -> str:
    per_scene = max(1.0, duration / 5)
    header = (
        f"Create a single 2D anime opening sequence (cel-shaded, hand-drawn look). "
        f"Total length: {duration} seconds. Aspect {aspect}. {GLOBAL_STYLE} "
        "Use sakuga-quality motion accents, tasteful speed lines and smear frames. "
        "Original character only; do not depict any real person's identifiable face or likeness; no brand/logos. "
        "Color script: deep blues + neon reds; slight film grain overlay for texture. "
        "Keep motion readable; avoid chaotic cutting."
    )

    if strict:
        header += (
            f" Strict timing: Final output length must be {duration}±0.5 seconds. "
            "Do not end early. If under-length, extend shot holds and linger on the title card to meet the duration. "
            "Keep cadence consistent; do not collapse multiple beats into a shorter montage."
        )

    if voice in ("narration", "voiceover"):
        header += (
            " Audio: Generate Japanese voice-over lines as instructed; natural, emotive Japanese voice (non-celebrity). "
            "Add subtle cinematic BGM (no vocals); automatically duck BGM under voice by ~8 dB."
        )

    parts = [
        (
            f"Beat 1 (~{per_scene}s): Extreme close-up of boxing glove brushing chalk dust; "
            f"dust shockwave freezes into ink-like splash forming an abstract kanji silhouette. "
            f"Snap tilt down, quick push-in; light blooms; speed lines parallax in the background."
            + ("\nVoice-over (Japanese): その夜、世界は変わる。" if voice else "")
        ),
        (
            f"Beat 2 (~{per_scene}s): Locker-room vibe. Close on protagonist 'Kai' lacing gloves; "
            f"orbiting camera; face kept stylized/generic. Warm key light, cool teal shadows; neon bokeh through window."
            + ("\nVoice-over (Japanese): 名前はカイ。怪物に、挑む。" if voice else "")
        ),
        (
            f"Beat 3 (~{per_scene}s): Training tempo rises: jump rope footwork with smear frames; "
            f"mitt work arcs leave speed lines; sweat catches rim light. Three readable match-move beats."
            + (
                "\nVoice-over (Japanese): 恐れは、踏み出す一歩で砕ける。"
                if voice
                else ""
            )
        ),
        (
            f"Beat 4 (~{per_scene}s): Walk-up tunnel to ring; rim-lit silhouette; light pulses like a heartbeat; "
            f"crowd abstracted as bokeh. Slow dolly-forward; epic but smooth."
            + ("\nVoice-over (Japanese): 歓声が、心臓の鼓動と重なる。" if voice else "")
        ),
        (
            f"Beat 5 (~{per_scene}s): In-ring abstract exchange: weave under hook, counter body shot lands—impact ripple with "
            f"radial speed lines and ink splash. Freeze-frame morphs into title card: 『{title}』. Minimal CTA placeholder."
            + ("\nVoice-over (Japanese): 一撃で、運命は動き出す。" if voice else "")
        ),
    ]

    return header + "\n" + "\n".join(parts)


def build_prompt_doc_trailer(
    title: str, duration: int, aspect: str, voice: str | None, strict: bool = False
) -> str:
    per_scene = max(1.0, duration / 5)
    header = (
        f"Create a single cinematic sports documentary trailer composed of 5 sequential shots; "
        f"Total length: {duration} seconds. Each shot ~{per_scene}s. Aspect {aspect}. {GLOBAL_STYLE} "
        "High-contrast arena lighting, warm tungsten highlights with cool teal shadows, rim light and light haze; subtle grain. "
        "Elite bantam/bantamweight boxer subject; focus on gloves, footwork, torso, and silhouettes; "
        "do not depict any specific real person's identifiable face; avoid logos. Hard cuts only."
    )
    if voice in ("narration", "voiceover"):
        header += (
            " Audio: Generate Japanese voice-over as instructed; natural calm male voice (mid-30s timbre). "
            "Add subtle cinematic BGM (no vocals); duck BGM under voice by ~8 dB."
        )

    if strict:
        header += (
            f" Strict timing: Final output length must be {duration}±0.5 seconds. "
            "Do not end early. If under-length, extend shot holds and linger on the final title card for ~2 seconds to meet the duration. "
            "Do not compress multiple shots into a shorter montage."
        )

    parts = [
        (
            f"Shot 1: Backstage tunnel before the fight. Close on taped hands tightening gloves; "
            f"slow dolly-in; breath visible in cool air; arena light leaks create warm rim light."
            + (
                "\nVoice-over (Japanese): 静かな通路に、鼓動だけが響く。"
                if voice
                else ""
            )
        ),
        (
            f"Shot 2: Training gym montage—jump rope footwork rhythm, mitt work with crisp punches; "
            f"dust motes glow in a light beam; analog wall clock ticks late at night."
            + (
                "\nVoice-over (Japanese): 敗北を抱え、彼らは戻る。静かなジムで、答えを探し続けた。"
                if voice
                else ""
            )
        ),
        (
            f"Shot 3: Corner and team. Mouthpiece placed; coach's hand on shoulder; a nod of trust; "
            f"camera arcs slowly; warm practical lights behind them."
            + (
                "\nVoice-over (Japanese): 勝負はひとりじゃない。背中には、信じてくれる人がいた。"
                if voice
                else ""
            )
        ),
        (
            f"Shot 4: International canvas hinting Mexico/Argentina via flags/signage (generic). "
            f"Camera glides along ropes: pivots, feints, level changes; spotlight carves a clean silhouette."
            + (
                "\nVoice-over (Japanese): 国が変われば、空気も変わる。それでも、リングの真ん中は同じだった。"
                if voice
                else ""
            )
        ),
        (
            f"Shot 5: Fight crescendo abstracted: slow-motion exchange; body shot lands; bell rings; "
            f"camera tilts to ceiling lights; settle on boxer alone on a stool—resolve rebuilt. Title: 『{title}』."
            + (
                "\nVoice-over (Japanese): 怪物に出会い、知った。強さは、倒れてなお立ち上がること。"
                if voice
                else ""
            )
        ),
    ]
    return header + "\n" + "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sora2 one-shot generator")
    ap.add_argument("--preset", choices=["anime_op", "doc_trailer"], required=True)
    ap.add_argument(
        "--title", required=True, help="作品タイトル（タイトルカードに使用）"
    )
    ap.add_argument("--aspect", default="9:16", help="例: 9:16, 16:9, 1:1")
    ap.add_argument("--duration", type=int, default=25, help="合計尺（秒）")
    ap.add_argument(
        "--voice",
        choices=["none", "narration"],
        default="narration",
        help="音声を生成（ナレーション+BGM）",
    )
    ap.add_argument(
        "--out",
        help="出力パス（.mp4）。未指定なら data/procecced/videos_sora/<title>/one_shot_<preset>.mp4",
    )
    ap.add_argument(
        "--strict-duration",
        action="store_true",
        help="尺の厳密遵守を強く指示（±0.5秒以内を要求）",
    )
    ap.add_argument(
        "--model", default="sora-2", help="使用モデル（例: sora-2, sora-2-pro）"
    )
    ap.add_argument(
        "--seconds",
        type=int,
        help="APIに送る希望尺（秒）。未指定なら duration を利用（対応クライアントのみ）",
    )
    ap.add_argument(
        "--size",
        help="解像度（例: 1080x1920, 1280x720）未指定時はアスペクトから自動設定（対応クライアントのみ）",
    )
    ap.add_argument(
        "--fast", action="store_true", help="高速プレビュー（低解像度・短尺・音声OFF）"
    )
    args = ap.parse_args()

    voice = None if args.voice == "none" else "narration"

    # 出力パス
    if args.out:
        out_path = Path(args.out)
    else:
        safe_title = args.title.replace("/", "_")
        base = Path("data/procecced/videos_sora") / safe_title
        base.mkdir(parents=True, exist_ok=True)
        out_path = base / f"one_shot_{args.preset}.mp4"

    # size の既定値（APIが受け付ける場合）
    def default_size_for_aspect(a: str) -> str:
        a = a.replace(" ", "")
        if a in ("9:16", "9/16"):
            # Non-pro supports 720x1280; pro supports 1024x1792
            return "1024x1792" if "pro" in args.model else "720x1280"
        if a in ("16:9", "16/9"):
            return "1792x1024" if "pro" in args.model else "1280x720"
        if a in ("1:1", "1/1"):
            # APIに1:1がないため未指定に近い安全値として縦を選択
            return "1024x1792" if "pro" in args.model else "720x1280"
        # フォールバック
        return "1024x1792" if "pro" in args.model else "720x1280"

    def small_size_for_aspect(a: str) -> str:
        a = a.replace(" ", "")
        if a in ("9:16", "9/16"):
            return "720x1280"
        if a in ("16:9", "16/9"):
            return "1280x720"
        return "720x1280"

    size_value = args.size or default_size_for_aspect(args.aspect)
    # seconds は一部モデルで '4'|'8'|'12' のみ許容されるケースがある
    allowed_seconds = {"4", "8", "12"}

    def choose_allowed_seconds(d: int) -> str:
        if d >= 12:
            return "12"
        if d >= 8:
            return "8"
        return "4"

    seconds_value: str | None = None
    if args.seconds is not None:
        # 明示指定がある場合はそのまま使うが、許容外なら無効化
        s_str = str(args.seconds)
        seconds_value = s_str if s_str in allowed_seconds else None
    else:
        # 未指定: pro系モデルでは近似で選択、それ以外は未指定（プロンプト寄せ）
        if "pro" in args.model:
            seconds_value = choose_allowed_seconds(args.duration)

    # 高速プレビュー適用
    strict_flag = args.strict_duration
    if args.fast:
        # 低解像度・短尺・音声OFF
        size_value = args.size or small_size_for_aspect(args.aspect)
        if "pro" in args.model:
            seconds_value = "8"
        voice = None
        strict_flag = False

    # プロンプト構築（fast/strict/voice適用後）
    if args.preset == "anime_op":
        prompt = build_prompt_anime_op(
            args.title, args.duration, args.aspect, voice, strict_flag
        )
    else:
        prompt = build_prompt_doc_trailer(
            args.title, args.duration, args.aspect, voice, strict_flag
        )

    print("=== 生成設定 ===")
    print(f"Preset      : {args.preset}")
    print(f"Title       : {args.title}")
    print(f"Aspect      : {args.aspect}")
    print(f"Duration    : {args.duration}s")
    print(f"Voice       : {'ON' if voice else 'OFF'}")
    print(f"Model       : {args.model}")
    print(f"API Seconds : {seconds_value if seconds_value else '(not set)'}")
    print(f"API Size    : {size_value}")
    print(f"Output      : {out_path}")
    print("\n--- Prompt ---\n" + prompt + "\n---------------")

    client = OpenAI()
    try:
        print("\n動画生成中... (数分かかります)")
        # まずは seconds/size を付けて試行（対応クライアント向け）
        try:
            if seconds_value:
                video = client.videos.create_and_poll(
                    model=args.model,
                    prompt=prompt,
                    seconds=seconds_value,
                    size=size_value,
                )
            else:
                video = client.videos.create_and_poll(
                    model=args.model,
                    prompt=prompt,
                    size=size_value,
                )
        except TypeError:
            # 古いクライアントや未対応の場合は最小引数で再試行
            video = client.videos.create_and_poll(
                model=args.model,
                prompt=prompt,
            )
        print("\n✓ 動画生成完了")
        print(f"  Video ID: {getattr(video, 'id', '?')}")
        print(f"  長さ: {getattr(video, 'seconds', '?')} 秒")

        print("動画をダウンロード中...")
        content = client.videos.download_content(video.id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)
        print(f"✓ 保存: {out_path}")
        return 0
    except Exception as e:
        print(f"✗ エラー: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
