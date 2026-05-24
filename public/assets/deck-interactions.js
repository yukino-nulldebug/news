(() => {
  const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const motionTargets = [
    ".slide",
    ".summary-card",
    ".highlight",
    ".panel",
    ".module-node",
    ".system-node",
    ".pipeline-step",
    ".flow-step",
    ".data-node",
    ".mode-node",
    ".phase-card",
    ".next-phase-card",
    ".check-card",
    ".function-card",
    ".rule-card",
    ".decision-card",
    ".comment-card",
    ".mermaid-panel",
    ".table-wrap",
    ".code-preview",
    ".doc-link"
  ].join(",");

  const flowGroups = [
    ".pipeline",
    ".phase-roadmap",
    ".next-phase-map",
    ".acceptance-flow",
    ".flow-rail",
    ".system-stack",
    ".module-stack",
    ".api-path"
  ];

  const itemSelector = [
    ".pipeline-step",
    ".phase-card",
    ".next-phase-card",
    ".check-card",
    ".flow-step",
    ".system-node",
    ".module-node",
    ".api-node"
  ].join(",");

  function revealOnScroll() {
    const targets = Array.from(document.querySelectorAll(motionTargets));
    targets.forEach((target, index) => {
      target.classList.add("motion-item");
      target.style.setProperty("--motion-delay", `${Math.min(index % 8, 7) * 45}ms`);
    });

    if (motionQuery.matches || !("IntersectionObserver" in window)) {
      targets.forEach((target) => target.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );

    targets.forEach((target) => observer.observe(target));
  }

  function animateFlowGroups() {
    if (motionQuery.matches) return;

    document.querySelectorAll(flowGroups.join(",")).forEach((group) => {
      const items = Array.from(group.querySelectorAll(itemSelector));
      if (items.length < 2) return;

      let currentIndex = 0;
      let timer = null;

      const setActive = () => {
        items.forEach((item, index) => {
          item.classList.toggle("is-active", index === currentIndex);
          item.classList.toggle("is-complete", index < currentIndex);
        });
        currentIndex = (currentIndex + 1) % items.length;
      };

      const start = () => {
        if (timer) return;
        setActive();
        timer = window.setInterval(setActive, 1400);
      };

      const stop = () => {
        if (!timer) return;
        window.clearInterval(timer);
        timer = null;
      };

      if (!("IntersectionObserver" in window)) {
        start();
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              start();
            } else {
              stop();
            }
          });
        },
        { threshold: 0.35 }
      );

      observer.observe(group);
    });
  }

  function attachScrubbers() {
    document.querySelectorAll("[data-step-control]").forEach((control) => {
      const targetId = control.getAttribute("data-step-control");
      const target = document.getElementById(targetId);
      if (!target) return;

      const steps = Array.from(target.querySelectorAll(itemSelector));
      if (!steps.length) return;

      control.setAttribute("min", "0");
      control.setAttribute("max", String(steps.length - 1));
      control.setAttribute("value", "0");

      const update = () => {
        const activeIndex = Number(control.value);
        steps.forEach((step, index) => {
          step.classList.toggle("is-active", index === activeIndex);
          step.classList.toggle("is-complete", index < activeIndex);
        });
      };

      control.addEventListener("input", update);
      update();
    });
  }

  window.addEventListener("DOMContentLoaded", () => {
    document.documentElement.classList.add("js-enabled");
    revealOnScroll();
    animateFlowGroups();
    attachScrubbers();
  });
})();
