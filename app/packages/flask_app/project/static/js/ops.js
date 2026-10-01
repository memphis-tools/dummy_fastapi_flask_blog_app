document.addEventListener("DOMContentLoaded", () => {

    "use strict";

    document
        .getElementById("ops-top")
        ?.classList.add("ops-js");

    const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    ).matches;


    /* =========================================================
       REVEAL ELEMENTS
    ========================================================== */
    const revealElements = document.querySelectorAll(".reveal");

    if ("IntersectionObserver" in window && !reduceMotion) {

        const revealObserver = new IntersectionObserver(
            (entries, observer) => {

                entries.forEach((entry) => {

                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);

                });

            },
            {
                threshold: 0.12,
                rootMargin: "0px 0px -7% 0px"
            }
        );

        revealElements.forEach((element) => {
            revealObserver.observe(element);
        });

    } else {

        revealElements.forEach((element) => {
            element.classList.add("is-visible");
        });

    }


    /* =========================================================
       HERO TERMINAL — rotating random commands
    ========================================================== */
    const HERO_COMMANDS = [
        "./explore_labs.sh --all",
        "vagrant up && ansible all -m ping",
        "terraform apply -auto-approve",
        "docker stack deploy -c stack.yml ops",
        "kubectl get pods -n crook-ops",
        "sudo journalctl -f -p warning"
    ];

    const heroCommand = document.querySelector(".js-hero-command");

    if (heroCommand) {

        if (reduceMotion) {

            heroCommand.textContent =
                HERO_COMMANDS[
                    Math.floor(Math.random() * HERO_COMMANDS.length)
                ];

        } else {

            let heroIndex =
                Math.floor(Math.random() * HERO_COMMANDS.length);

            const typeHero = async () => {

                const command = HERO_COMMANDS[heroIndex];

                for (let i = 0; i < command.length; i += 1) {

                    heroCommand.textContent += command[i];
                    await new Promise((resolve) =>
                        window.setTimeout(resolve, 46)
                    );

                }

                await new Promise((resolve) =>
                    window.setTimeout(resolve, 3400)
                );

                for (let i = command.length; i >= 0; i -= 2) {

                    heroCommand.textContent =
                        command.slice(0, i);
                    await new Promise((resolve) =>
                        window.setTimeout(resolve, 12)
                    );

                }

                heroIndex =
                    (heroIndex + 1) % HERO_COMMANDS.length;

                typeHero();

            };

            window.setTimeout(typeHero, 500);

        }

    }


    /* =========================================================
       TERMINAL ENGINE (fixed size, clean & retype loop)
    ========================================================== */
    const wait = (milliseconds) =>
        new Promise((resolve) => window.setTimeout(resolve, milliseconds));


    async function typeText(element, text, speed = 26) {

        element.textContent = "";

        if (reduceMotion) {
            element.textContent = text;
            return;
        }

        for (const character of text) {

            element.textContent += character;
            await wait(speed);

        }

    }


    async function runTerminal(terminal) {

        const script = terminal.querySelector("[data-terminal-script]");

        if (!script) {
            return;
        }

        let lines = [];

        try {
            lines = JSON.parse(script.dataset.lines || "[]");
        } catch (error) {
            console.error("Invalid terminal script:", error);
            return;
        }

        if (!lines.length) {
            return;
        }

        do {

            script.innerHTML = "";

            for (const line of lines) {

                const commandLine = document.createElement("p");
                commandLine.className = "terminal-command-line";

                const prompt = document.createElement("b");
                prompt.textContent = line.prompt || "$ ";

                const command = document.createElement("span");

                commandLine.append(prompt, command);
                script.appendChild(commandLine);

                await typeText(command, line.text || "");

                if (line.output) {

                    await wait(reduceMotion ? 0 : 140);

                    const output = document.createElement("pre");
                    output.className = "terminal-output";
                    output.textContent = line.output;

                    script.appendChild(output);

                }

                await wait(reduceMotion ? 0 : 400);

                script.scrollTop = script.scrollHeight;

            }

            if (reduceMotion || terminal.dataset.terminalLoop !== "true") {
                break;
            }

            await wait(3200);

        } while (true);

    }


    document.querySelectorAll("[data-terminal]").forEach((terminal) => {

        let started = false;

        const start = () => {

            if (started) {
                return;
            }

            started = true;
            runTerminal(terminal);

        };

        if (!("IntersectionObserver" in window) || reduceMotion) {

            start();

        } else {

            const observer = new IntersectionObserver(
                (entries) => {

                    if (entries.some((entry) => entry.isIntersecting)) {
                        start();
                        observer.disconnect();
                    }

                },
                {
                    threshold: 0.25
                }
            );

            observer.observe(terminal);

        }

    });

    /* =========================================================
       PROSE CYCLER v3 — single permanent slot, fixed height,
       type → hold → fade → next → loop. Zero layout impact.
    ========================================================== */
    document.querySelectorAll(".js-prose").forEach((container) => {

        const sources =
            Array.from(container.querySelectorAll("p"));

        if (!sources.length || reduceMotion) {
            return;
        }

        const originals =
            sources.map((p) => p.textContent.trim());

        /* build the one permanent slot */
        const slot = document.createElement("p");
        slot.className = "is-slot";
        container.prepend(slot);

        let started = false;

        const readingTime = (text) =>
            Math.max(2400, Math.min(7000, text.length * 32));

        const typeIntoSlot = async (text) => {

            const span = document.createElement("span");
            span.className = "prose-text";

            slot.textContent = "";
            slot.appendChild(span);

            for (const character of text) {

                span.textContent += character;

                /* newest line always visible; overflow
                   scrolls off the top like a terminal */
                slot.scrollTop = slot.scrollHeight;

                await wait(14);

            }

        };

        const cycle = async () => {

            if (started) {
                return;
            }

            started = true;

            let index = 0;

            while (true) {

                slot.classList.add("is-typing");
                slot.classList.remove("is-fading");
                slot.scrollTop = 0;

                await typeIntoSlot(originals[index]);

                slot.classList.remove("is-typing");

                await wait(readingTime(originals[index]));

                slot.classList.add("is-fading");

                await wait(420);

                index = (index + 1) % originals.length;

                await wait(180);

            }

        };

        if (!("IntersectionObserver" in window)) {
            cycle();
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {

                if (entries.some((entry) => entry.isIntersecting)) {
                    cycle();
                    observer.disconnect();
                }

            },
            {
                threshold: 0.15
            }
        );

        observer.observe(container);

    });

    /* =========================================================
       COUNTERS — replay from 0 on EVERY view, slow easing
    ========================================================== */
    document.querySelectorAll(".js-counter").forEach((counter) => {

        const finalValue = Number(counter.dataset.counter || 0);
        const suffix = counter.dataset.suffix || "";

        if (finalValue <= 0 || reduceMotion) {
            counter.textContent = `${finalValue}${suffix}`;
            return;
        }

        const animate = () => {

            const duration = 2600;
            const startTime = performance.now();

            const frame = (time) => {

                const progress = Math.min(
                    (time - startTime) / duration,
                    1
                );

                const eased =
                    1 - Math.pow(1 - progress, 4);

                counter.textContent =
                    `${Math.floor(finalValue * eased)}${suffix}`;

                if (progress < 1) {
                    requestAnimationFrame(frame);
                } else {
                    counter.textContent = `${finalValue}${suffix}`;
                    counter.classList.add("is-done");
                }

            };

            requestAnimationFrame(frame);

        };

        const observer = new IntersectionObserver(
            (entries) => {

                entries.forEach((entry) => {

                    if (entry.isIntersecting) {
                        counter.classList.remove("is-done");
                        animate();
                    }

                });

            },
            {
                threshold: 0.6
            }
        );

        observer.observe(counter);

    });


    /* =========================================================
       REUSABLE CAROUSELS + AUTO-SCROLL + SYNC PROGRESS BAR
    ========================================================== */
    document.querySelectorAll("[data-carousel]").forEach((carousel) => {

        const track = carousel.querySelector(".carousel-track");

        const slides = Array.from(
            carousel.querySelectorAll(".carousel-slide")
        );

        const previous =
            carousel.querySelector("[data-carousel-prev]");

        const next =
            carousel.querySelector("[data-carousel-next]");

        const currentLabel =
            carousel.querySelector("[data-carousel-current]");

        const totalLabel =
            carousel.querySelector("[data-carousel-total]");

        const dotsContainer =
            carousel.querySelector("[data-carousel-dots]");

        const progressBar =
            carousel.querySelector(".carousel-progress span");

        if (!track || !slides.length) {
            return;
        }

        let current = 0;
        let touchStart = null;
        let autoTimer = null;
        let autoPaused = false;

        const AUTO_DELAY = Number(
            carousel.dataset.autoscroll || 6000
        );

        if (totalLabel) {
            totalLabel.textContent =
                String(slides.length).padStart(2, "0");
        }

        if (progressBar) {
            progressBar.style.animationDuration = `${AUTO_DELAY}ms`;
        }


        const dots = [];

        if (dotsContainer) {

            slides.forEach((slide, index) => {

                const button = document.createElement("button");

                button.type = "button";
                button.className = "carousel-dot";

                button.setAttribute(
                    "aria-label",
                    `Show item ${index + 1}`
                );

                button.addEventListener("click", () => {
                    show(index);
                    restartAuto();
                });

                dotsContainer.appendChild(button);
                dots.push(button);

            });

        }


        function show(index) {

            current =
                (index + slides.length) % slides.length;

            track.style.transform =
                `translate3d(-${current * 100}%, 0, 0)`;

            slides.forEach((slide, slideIndex) => {

                const active = slideIndex === current;

                slide.classList.toggle("is-active", active);

                slide.setAttribute(
                    "aria-hidden",
                    active ? "false" : "true"
                );

            });

            dots.forEach((dot, dotIndex) => {

                dot.classList.toggle(
                    "is-active",
                    dotIndex === current
                );

            });

            if (currentLabel) {
                currentLabel.textContent =
                    String(current + 1).padStart(2, "0");
            }

        }


        function startAuto() {

            if (reduceMotion || AUTO_DELAY <= 0) {
                return;
            }

            autoTimer = window.setInterval(() => {

                if (!autoPaused && !document.hidden) {
                    show(current + 1);
                }

            }, AUTO_DELAY);

        }


        function stopAuto() {

            if (autoTimer !== null) {
                window.clearInterval(autoTimer);
                autoTimer = null;
            }

        }


        function restartAuto() {

            stopAuto();

            if (progressBar) {

                progressBar.style.animation = "none";

                window.requestAnimationFrame(() => {
                    progressBar.style.animation = "";
                });

            }

            startAuto();

        }


        previous?.addEventListener("click", () => {
            show(current - 1);
            restartAuto();
        });

        next?.addEventListener("click", () => {
            show(current + 1);
            restartAuto();
        });


        carousel.addEventListener("mouseenter", () => {
            autoPaused = true;
        });

        carousel.addEventListener("mouseleave", () => {
            autoPaused = false;
        });

        carousel.addEventListener("focusin", () => {
            autoPaused = true;
        });

        carousel.addEventListener("focusout", () => {
            autoPaused = false;
        });


        carousel.tabIndex = 0;

        carousel.addEventListener("keydown", (event) => {

            if (event.key === "ArrowLeft") {
                event.preventDefault();
                show(current - 1);
                restartAuto();
            }

            if (event.key === "ArrowRight") {
                event.preventDefault();
                show(current + 1);
                restartAuto();
            }

        });


        carousel.addEventListener(
            "touchstart",
            (event) => {
                touchStart = event.changedTouches[0].clientX;
                autoPaused = true;
            },
            { passive: true }
        );


        carousel.addEventListener(
            "touchend",
            (event) => {

                if (touchStart === null) {
                    return;
                }

                const difference =
                    event.changedTouches[0].clientX - touchStart;

                if (Math.abs(difference) > 45) {

                    show(
                        difference > 0
                            ? current - 1
                            : current + 1
                    );

                    restartAuto();

                }

                touchStart = null;
                autoPaused = false;

            },
            { passive: true }
        );

        show(0);
        startAuto();

    });


    /* =========================================================
       PIPELINE SCENARIOS — typed console, coherent commands
    ========================================================== */
    const SCENARIOS = [
        {
            name: "TOMCAT STANDALONE",
            steps: ["GITHUB", "JENKINS", "ALB"],
            lines: [
                { tag: "[SCM]", text: "GitHub webhook received — push on main" },
                { tag: "[JENKINS]", text: "pipeline crook-ops-tomcat triggered" },
                { tag: "[MAVEN]", text: "mvn clean package -DskipTests → crook-ops.war" },
                { tag: "[TEST]", text: "mvn test — 42 tests, 0 failures" },
                { tag: "[ANSIBLE]", text: "ansible-playbook deploy_war.yml -l tomcat-ec2" },
                { tag: "[DEPLOY]", text: "scp crook-ops.war tomcat@10.0.1.15:/opt/tomcat/webapps/" },
                { tag: "[ALB]", text: "listener rule: /mysite → target-group tomcat-ec2" },
                { tag: "[OK]", text: "https://alb.aws/mysite — deployment live" }
            ]
        },
        {
            name: "DOCKER CONTAINER",
            steps: ["GITHUB", "JENKINS", "ANSIBLE", "DOCKERHUB", "DOCKER"],
            lines: [
                { tag: "[SCM]", text: "GitHub webhook received — push on main" },
                { tag: "[JENKINS]", text: "pipeline crook-ops-docker triggered" },
                { tag: "[BUILD]", text: "docker build -t memphistools/crook-ops:latest ." },
                { tag: "[ANSIBLE]", text: "ansible-playbook build_push.yml — docker login + push" },
                { tag: "[DOCKERHUB]", text: "docker push memphistools/crook-ops:latest" },
                { tag: "[ANSIBLE]", text: "ansible-playbook deploy_container.yml -l docker-ec2" },
                { tag: "[DOCKER]", text: "docker run -d -p 8080:8080 memphistools/crook-ops" },
                { tag: "[ALB]", text: "listener rule: /docker/mysite → tg docker-ec2" },
                { tag: "[OK]", text: "https://alb.aws/docker/mysite — container live" }
            ]
        },
        {
            name: "KUBERNETES EKS",
            steps: ["GITHUB", "JENKINS", "ANSIBLE", "DOCKERHUB", "EKS"],
            lines: [
                { tag: "[SCM]", text: "GitHub webhook received — push on main" },
                { tag: "[JENKINS]", text: "pipeline crook-ops-k8s triggered" },
                { tag: "[ANSIBLE]", text: "ansible-playbook eks_control.yml -l eks-bastion" },
                { tag: "[EKSCTL]", text: "eksctl create cluster --name crook --nodes 2" },
                { tag: "[K8S]", text: "kubectl apply -f manifests/ — deployment 3 replicas" },
                { tag: "[K8S]", text: "kubectl rollout status deploy/crook-ops — 3/3 ready" },
                { tag: "[SVC]", text: "kubectl expose deploy crook-ops --type NodePort" },
                { tag: "[ALB]", text: "listener rule: /k8s/mysite → tg eks-nodeport" },
                { tag: "[OK]", text: "https://alb.aws/k8s/mysite — pods serving" }
            ]
        },
        {
            name: "STATIC APP PLATFORM",
            steps: ["GITHUB"],
            lines: [
                { tag: "[SCM]", text: "GitHub webhook received — push on main" },
                { tag: "[DO]", text: "DigitalOcean App Platform detected static site" },
                { tag: "[BUILD]", text: "auto-build from repo — no pipeline host needed" },
                { tag: "[CDN]", text: "assets pushed to DO edge — TLS by default" },
                { tag: "[OK]", text: "https://crook-ops.ondigitalocean.app — live" }
            ]
        }
    ];


    const pipelineConsole =
        document.querySelector("[data-pipeline-console]");

    const pipelineSteps =
        Array.from(document.querySelectorAll(
            "[data-pipeline] .pipeline-step"
        ));


    function highlightSteps(activeNames) {

        pipelineSteps.forEach((step) => {

            const name =
                step.querySelector("b")?.textContent || "";

            step.classList.toggle(
                "is-active",
                activeNames.includes(name)
            );

        });

    }


    async function runScenarios() {

        let scenarioIndex = 0;

        do {

            const scenario = SCENARIOS[scenarioIndex];

            if (pipelineConsole) {

                pipelineConsole.innerHTML = "";

                const label = document.createElement("p");

                label.innerHTML =
                    `<span class="pipeline-scenario-label">` +
                    `SCENARIO — ${scenario.name}</span>`;

                pipelineConsole.appendChild(label);

                if (!reduceMotion) {
                    await wait(500);
                }

                for (const line of scenario.lines) {

                    const p = document.createElement("p");
                    p.className = "is-typing";

                    const tag = document.createElement("span");
                    tag.textContent = `${line.tag} `;

                    const cmd = document.createElement("span");
                    cmd.className = "cmd";

                    p.append(tag, cmd);
                    pipelineConsole.appendChild(p);

                    if (reduceMotion) {

                        cmd.textContent = line.text;

                    } else {

                        for (const character of line.text) {
                            cmd.textContent += character;
                            await wait(16);
                        }

                        p.classList.remove("is-typing");

                    }

                }

            }

            highlightSteps(scenario.steps);

            await wait(reduceMotion ? 6000 : 5200);

            scenarioIndex = (scenarioIndex + 1) % SCENARIOS.length;

        } while (true);

    }


    if (pipelineConsole) {

        if (reduceMotion) {
            runScenarios();
        } else {

            const observer = new IntersectionObserver(
                (entries) => {

                    if (entries.some((entry) => entry.isIntersecting)) {
                        runScenarios();
                        observer.disconnect();
                    }

                },
                { threshold: 0.3 }
            );

            observer.observe(pipelineConsole);

        }

    }


    /* =========================================================
       TECH RADAR — 30s rotation, blur, NEWS-RELATED images
    ========================================================== */
    const NEWS_POOL = [
        {
            tag: "AI / MODEL RELEASE",
            title: "OpenAI rolls out GPT-6.1 Sol at DevDay 2026",
            summary:
                "At its annual DevDay, OpenAI introduced GPT-6.1 Sol — " +
                "one week after its predecessor GPT-6 Sol — alongside " +
                "new 'Dots' agents, a price drop on the new model, and " +
                "comments from Altman and CFO Sarah Friar on a widely " +
                "expected IPO.",
            image:
                "https://image.cnbcfm.com/api/v1/image/108369815-1790712597213-" +
                "gettyimages-2297765991-_04a9178_m4u5cgwo.jpeg" +
                "?v=1790712953&w=1200&h=675",
            link: "https://www.cnbc.com/amp/2026/09/29/openai-devday-2026-live-updates.html",
            credit: "Image & story: CNBC — OpenAI DevDay 2026"
        },
        {
            tag: "CYBERSECURITY / CRITICAL",
            title: "Citrix NetScaler DTLS flaw actively exploited in the wild",
            summary:
                "CVE-2026-88772 (CVSS 9.5), a memory overflow bug in " +
                "DTLS handling inside the NetScaler Packet Processing " +
                "Engine, and CVE-2026-88771 (unauthenticated RCE) were " +
                "both added to CISA's Known Exploited Vulnerabilities " +
                "catalog after reports of broad, opportunistic " +
                "exploitation affecting dozens of organizations.",
            image:
                "https://thehackernews.com/images/-AaptImXE5Y4/WzjvqBS8HtI/" +
                "AAAAAAAAxSs/BcCIwpWJszILkuEbDfKZhxQJwOAD7qV6ACLcBGAs/" +
                "s728-e365/the-hacker-news.jpg",
            link: "https://thehackernews.com/search/label/Vulnerability",
            credit: "Image & story: The Hacker News / CISA KEV"
        },
        {
            tag: "SECURITY / ZERO-DAY",
            title: "WordPress flaw exploited within hours of disclosure",
            summary:
                "CVE-2026-87902 (CVSS 9.2) allows unauthenticated " +
                "remote code execution in WordPress under specific " +
                "theme and server conditions. Honeypots recorded " +
                "exploitation attempts within hours of disclosure — " +
                "weaponizing pearcmd.php to write PHP files — and " +
                "CISA added the flaw to its KEV catalog with a " +
                "three-day remediation deadline.",
            image:
                "https://blogger.googleusercontent.com/img/b/R29vZ2xl/" +
                "AVvXsEizoRcyQE1N3fGUKa2FY_q_T7EG_CyjTpMGGk1oFUF-XpBZa0zCA6V2yEuv3_" +
                "Z1OrEjMmhbZdaVmo6NMrwb98U9VFGXDpRcItboVuZH7qc9QgPd5ZLDudfJPWoaSDbtkoXJeLTZw-6JDbq5F6YEp4AkeoJd10Nb_H9tuU0fYdgqkLrP6BTpAPOYwO6WdmkN/" +
                "s1700-nu-rw-lo-l85-e365/wordpress-exploits.jpg",
            link: "https://thehackernews.com/2026/09/attackers-exploit-wordpress-cve-2026.html",
            credit: "Image & story: The Hacker News — WordPress exploitation"
        },
        {
            tag: "OS / PATCHING",
            title: "Microsoft Patch Tuesday crosses 400 CVEs a month",
            summary:
                "August 2026 Patch Tuesday fixed 421 CVEs, including " +
                "a use-after-free zero-day in the Ancillary Function " +
                "Driver for WinSock (afd.sys) exploited in the wild — " +
                "and researchers say the higher volumes are the new " +
                "normal. Rapid7 notes no reason to expect a return " +
                "to pre-2026 levels.",
            image:
                "https://www.securityweek.com/wp-content/uploads/2023/12/" +
                "Microsoft-Security-leaders.jpg",
            link: "https://www.securityweek.com/august-2026-patch-tuesday-microsoft-fixes-421-cves-one-exploited-zero-day/",
            credit: "Image & story: SecurityWeek / Rapid7"
        },
        {
            tag: "AI / BENCHMARKS",
            title: "Frontier model wave: 20+ releases and halved prices",
            summary:
                "September 2026 saw five frontier launches in ten days " +
                "(Claude Fable 5.1, GPT-6 Astra, Gemini 3.8 Flash, " +
                "Muse Spark 1.3, DeepSeek V4.1-Flash), followed by " +
                "Claude Opus 5.5, GPT-6 Sol and Luna, and Grok 4.7 — " +
                "with flagship prices roughly halved and a new $0.10 " +
                "per million token floor on the market.",
            image:
                "https://local-ai-zone.github.io/blog/" +
                "september-2026-ai-model-updates-hero.png",
            link: "https://local-ai-zone.github.io/blog/September_2026_AI_Model_Updates.html",
            credit: "Image & story: Local AI Zone — Sept 2026 dispatch"
        },
        {
            tag: "HOMELAB CULTURE",
            title: "Your homelab is a security boundary — treat it like one",
            summary:
                "Consumer-grade routers keep landing in CISA's KEV " +
                "catalog. The latest: a MikroTik RouterOS flaw allowing " +
                "unauthenticated clients to open a session channel and " +
                "send an exec request, chainable into full compromise. " +
                "A reminder for every Proxmox/Vagrant tinkerer: patch, " +
                "segment, and audit — even in the lab.",
            image:
                "https://www.cisa.gov/sites/default/files/styles/" +
                "banner/public/CISA_GOLD_BANNER.jpg",
            link: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            credit: "Story: CISA KEV catalog"
        }
    ];


    const newsTag =
        document.querySelector("[data-news-tag]");

    const newsTitle =
        document.querySelector("[data-news-title]");

    const newsSummary =
        document.querySelector("[data-news-summary]");

    const newsImage =
        document.querySelector("[data-news-image]");

    const newsCredit =
        document.querySelector("[data-news-credit]");

    const newsLink =
        document.querySelector("[data-news-link]");

    const newsBody =
        document.querySelector("[data-news-item]");

    const pickButton =
        document.getElementById("news-pick");

    const newsProgress =
        document.querySelector(".news-progress span");

    let lastNewsIndex = -1;


    function applyNews(index) {

        const item = NEWS_POOL[index];

        newsTag.textContent = item.tag;
        newsTitle.textContent = item.title;
        newsSummary.textContent = item.summary;

        if (newsImage) {
            newsImage.src = item.image;
            newsImage.alt = item.title;
        }

        if (newsCredit) {
            newsCredit.textContent = item.credit;
        }

        if (newsLink) {
            newsLink.href = item.link;
            newsLink.textContent = "READ THE SOURCE";
        }

    }


    function restartNewsProgress() {

        if (!newsProgress || reduceMotion) {
            return;
        }

        newsProgress.style.animation = "none";

        window.requestAnimationFrame(() => {
            newsProgress.style.animation = "";
        });

    }


    function showRandomNews(instant = false) {

        if (!newsTag || !newsTitle || !newsSummary) {
            return;
        }

        let index = lastNewsIndex;

        if (NEWS_POOL.length > 1) {

            while (index === lastNewsIndex) {
                index = Math.floor(
                    Math.random() * NEWS_POOL.length
                );
            }

        } else {
            index = 0;
        }

        lastNewsIndex = index;

        restartNewsProgress();

        if (instant || reduceMotion || !newsBody) {
            applyNews(index);
            return;
        }

        newsBody.classList.add("is-blurred");

        window.setTimeout(() => {

            applyNews(index);
            newsBody.classList.remove("is-blurred");

        }, 450);

    }


    pickButton?.addEventListener("click", () => {
        showRandomNews();
    });

    showRandomNews(true);

    window.setInterval(() => {
        showRandomNews();
    }, 30000);


    /* =========================================================
       PROXMOX — ROTATING LAB SCHEMES, 20s
    ========================================================== */
    const SCHEMES = [
        {
            label: "CLUSTER TOPOLOGY",
            sub: "WITH CEPH",
            caption:
                "Proxmox since v6 — today two nodes + Odroid NAS, " +
                "Ceph under evaluation for distributed storage.",
            nodes: [
                { icon: "fa-server", name: "NODE 01", sub: "PROXMOX" },
                { icon: "fa-server", name: "NODE 02", sub: "PROXMOX" },
                { icon: "fa-hard-drive", name: "ODROID / NAS", sub: "SNAPSHOTS" },
                { icon: "fa-database", name: "CEPH", sub: "LEARNING / EVAL" }
            ]
        },
        {
            label: "LAB / EGRESS PATH",
            sub: "SQUID + OPENVPN",
            caption:
                "Every VM reaches the Internet through Squid — the only " +
                "one allowed to talk to OpenVPN, the sole egress to the " +
                "outside world.",
            nodes: [
                { icon: "fa-cubes", name: "LAB VMS", sub: "17 MACHINES" },
                { icon: "fa-forward", name: "SQUID", sub: "PROXY / SSL BUMP" },
                { icon: "fa-lock", name: "OPENVPN", sub: "EGRESS ONLY" },
                { icon: "fa-globe", name: "INTERNET", sub: "OUTSIDE" }
            ]
        },
        {
            label: "LAB / FLEET CONTROL",
            sub: "ANSIBLE",
            caption:
                "One Ansible host addresses every machine — patching, " +
                "configuration drift, and role enforcement across the " +
                "whole laboratory.",
            nodes: [
                { icon: "fa-gears", name: "ANSIBLE", sub: "CONTROL NODE" },
                { icon: "fa-cubes", name: "DNS / KDC", sub: "IDENTITY" },
                { icon: "fa-cubes", name: "WEB / MAIL", sub: "SERVICES" },
                { icon: "fa-cubes", name: "STORAGE", sub: "NAS / BACKUP" }
            ]
        },
        {
            label: "LAB / DNS TRUST",
            sub: "DNSSEC / DANE / TLSA",
            caption:
                "Signed zones, TLSA records, DANE-validated TLS — the " +
                "lab tests mail and web flows that refuse unauthenticated " +
                "certificates.",
            nodes: [
                { icon: "fa-signature", name: "DNS PRIMARY", sub: "SIGNED ZONE" },
                { icon: "fa-signature", name: "DNS SECONDARY", sub: "TSIG TRANSFER" },
                { icon: "fa-fingerprint", name: "TLSA", sub: "DANE RECORDS" },
                { icon: "fa-envelope", name: "DOVECOT", sub: "MTA-STS / DANE" }
            ]
        },
        {
            label: "LAB / BACKUP",
            sub: "BACULA",
            caption:
                "Every machine carries a file pattern to be saved. " +
                "The Bacula director schedules, the storage daemon " +
                "archives to the NAS.",
            nodes: [
                { icon: "fa-clock-rotate-left", name: "DIRECTOR", sub: "SCHEDULER" },
                { icon: "fa-cubes", name: "FILE DAEMONS", sub: "EACH VM" },
                { icon: "fa-hard-drive", name: "STORAGE DAEMON", sub: "ARCHIVE" },
                { icon: "fa-box-archive", name: "ODROID / NAS", sub: "RETENTION" }
            ]
        }
    ];


    const schemeTitle =
        document.querySelector("[data-scheme-title]");

    const schemeSub =
        document.querySelector("[data-scheme-sub]");

    const schemeCaption =
        document.querySelector("[data-scheme-caption]");

    const schemeStage =
        document.querySelector("[data-scheme-stage]");

    let schemeIndex = 0;
    let schemeBuilt = false;


    function renderScheme(scheme) {

        if (!schemeStage) {
            return;
        }

        schemeStage.innerHTML = "";

        scheme.nodes.forEach((node, index) => {

            const nodeElement = document.createElement("div");
            nodeElement.className = "cluster-node scheme-node";

            const icon = document.createElement("i");
            icon.className = node.icon;

            const strong = document.createElement("strong");
            strong.textContent = node.name;

            const small = document.createElement("small");
            small.textContent = node.sub;

            nodeElement.append(icon, strong, small);

            schemeStage.appendChild(nodeElement);

            if (index < scheme.nodes.length - 1) {

                const connector = document.createElement("div");

                connector.className = "cluster-connection";
                connector.innerHTML = "<span></span>";

                schemeStage.appendChild(connector);

            }

        });

        if (schemeTitle) {
            schemeTitle.textContent = scheme.label;
        }

        if (schemeSub) {
            schemeSub.textContent = scheme.sub;
        }

        if (schemeCaption) {
            schemeCaption.textContent = scheme.caption;
        }

    }


    function rotateScheme() {

        if (!schemeStage) {
            return;
        }

        const scheme = SCHEMES[schemeIndex];

        if (reduceMotion || !schemeBuilt) {

            renderScheme(scheme);

        } else {

            schemeStage.classList.add("is-blurred");

            window.setTimeout(() => {

                renderScheme(scheme);
                schemeStage.classList.remove("is-blurred");

            }, 450);

        }

        schemeBuilt = true;
        schemeIndex = (schemeIndex + 1) % SCHEMES.length;

    }


    if (schemeStage) {

        rotateScheme();

        window.setInterval(rotateScheme, 20000);

    }


    /* =========================================================
       QUOTE ROTATOR
    ========================================================== */
    const QUOTES = [
        {
            text: "I speak attacker fluently. Nowadays I point the tools at vulnerabilities, not people.",
            author: "SANJURO, REFORMED"
        },
        {
            text: "A firewall is a strategy. A rule is a tactic. Know which one you are writing.",
            author: "GEN. R. OKONKWO, BLUE TEAM DOCTRINE"
        },
        {
            text: "The attacker needs one mistake. The defender needs one habit: verify everything.",
            author: "CMDR. E. VASQUEZ, SOC NIGHT SHIFT"
        },
        {
            text: "Offense informs defense. Silence informs nothing. Share your post-mortems.",
            author: "A. LAURENT, INCIDENT RESPONDER"
        },
        {
            text: "Every port you leave open is a sentence in a story an attacker will happily finish.",
            author: "K. NAKAMURA, NETWORK SENTINEL"
        },
        {
            text: "Backups are not an infrastructure choice. They are a promise to your future self.",
            author: "M. DIALLO, RESILIENCE ENGINEER"
        },
        {
            text: "Patch Tuesday is a date. Attack Wednesday is also a date. Be ready for both.",
            author: "R. STEINER, VULN MANAGEMENT"
        },
        {
            text: "Defense in depth means the attacker must be right many times. You must be right once — every day.",
            author: "COL. V. PETROVA, RED vs BLUE ARBITER"
        }
    ];


    const quoteText =
        document.querySelector("[data-quote-text]");

    const quoteAuthor =
        document.querySelector("[data-quote-author]");

    const quoteBox =
        document.querySelector("[data-quote-box]");

    let quoteIndex = 0;


    function rotateQuote() {

        if (!quoteText || !quoteAuthor) {
            return;
        }

        const quote = QUOTES[quoteIndex];

        const apply = () => {
            quoteText.textContent = quote.text;
            quoteAuthor.textContent = quote.author;
        };

        if (reduceMotion || !quoteBox) {

            apply();

        } else {

            quoteBox.classList.add("is-blurred");

            window.setTimeout(() => {

                apply();
                quoteBox.classList.remove("is-blurred");

            }, 450);

        }

        quoteIndex = (quoteIndex + 1) % QUOTES.length;

    }


    if (quoteText) {

        rotateQuote();

        window.setInterval(rotateQuote, 9000);

    }


    /* =========================================================
       FIXED SCROLL CONTROLS
    ========================================================== */
    const screens = Array.from(
        document.querySelectorAll(".ops-screen")
    );


    function nearestScreenIndex() {

        let closestIndex = 0;
        let closestDistance = Infinity;

        screens.forEach((screen, index) => {

            const distance =
                Math.abs(screen.getBoundingClientRect().top);

            if (distance < closestDistance) {

                closestDistance = distance;
                closestIndex = index;

            }

        });

        return closestIndex;

    }


    function scrollToScreen(index) {

        if (!screens.length) {
            return;
        }

        const safeIndex =
            Math.max(0, Math.min(index, screens.length - 1));

        screens[safeIndex].scrollIntoView({
            behavior: reduceMotion ? "auto" : "smooth",
            block: "start"
        });

    }


    document
        .querySelectorAll("[data-scroll-action]")
        .forEach((button) => {

            button.addEventListener("click", () => {

                const action = button.dataset.scrollAction;

                const current = nearestScreenIndex();

                if (action === "top") {
                    scrollToScreen(0);
                } else if (action === "bottom") {
                    scrollToScreen(screens.length - 1);
                } else if (action === "up") {
                    scrollToScreen(current - 1);
                } else if (action === "down") {
                    scrollToScreen(current + 1);
                }

            });

        });


    /* =========================================================
       ACTIVE SCREEN MARKER
    ========================================================== */
    if ("IntersectionObserver" in window) {

        const sectionObserver = new IntersectionObserver(
            (entries) => {

                entries.forEach((entry) => {

                    if (!entry.isIntersecting) {
                        return;
                    }

                    screens.forEach((screen) => {
                        screen.classList.remove("is-current-screen");
                    });

                    entry.target.classList.add("is-current-screen");

                });

            },
            {
                threshold: 0.5
            }
        );

        screens.forEach((screen) => {
            sectionObserver.observe(screen);
        });

    }

});
