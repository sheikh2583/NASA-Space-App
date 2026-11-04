import { Component, type ReactNode } from "react";
import i18n from "i18next";

export default class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed
      ? <section className="card"><p className="warn">{i18n.t("error.panel")}</p></section>
      : this.props.children;
  }
}
