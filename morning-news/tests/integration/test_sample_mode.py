from __future__ import annotations

import main as main_module


def test_main_sample_mode_generates_report_and_log(monkeypatch, sample_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: sample_settings)

    exit_code = main_module.main()

    report_path = sample_settings.report_dir / "2026-05-26.md"
    log_path = sample_settings.log_dir / "app.log"
    assert exit_code == 0
    assert report_path.exists()
    assert log_path.exists()

    report_text = report_path.read_text(encoding="utf-8")
    assert "## 2. 国内ニュース" in report_text
    assert "## 3. 海外ニュース" in report_text
    assert "## 4. マーケット情報" in report_text
    assert "## 5. 市況コメント" in report_text
    assert "## 6. 注意事項" in report_text

    log_text = log_path.read_text(encoding="utf-8")
    assert "F-01" in log_text
    assert "F-10" in log_text


def test_main_sample_mode_can_run_twice(monkeypatch, sample_settings):
    monkeypatch.setattr(main_module, "load_settings", lambda: sample_settings)

    assert main_module.main() == 0
    assert main_module.main() == 0
    assert (sample_settings.report_dir / "2026-05-26.md").exists()
