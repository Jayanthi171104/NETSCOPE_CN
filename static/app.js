let allPackets = [];

let refreshTimer = null;


document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadSystem();

        loadPackets();

        loadStatistics();

        startRefreshing();

    }
);


/* NAVIGATION */

function showSection(sectionId) {

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove(
                "active"
            );

        });


    const selected =
        document.getElementById(
            sectionId
        );


    if (selected) {

        selected.classList.add(
            "active"
        );

    }


    document
        .querySelectorAll(".nav-item")
        .forEach(button => {

            button.classList.remove(
                "active"
            );

        });


    const buttons =
        document.querySelectorAll(
            ".nav-item"
        );


    buttons.forEach(button => {

        if (
            button
                .textContent
                .toLowerCase()
                .includes(
                    sectionId === "dashboard"
                        ? "dashboard"
                        : sectionId === "packets"
                        ? "packets"
                        : sectionId === "statistics"
                        ? "statistics"
                        : "system"
                )
        ) {

            button.classList.add(
                "active"
            );

        }

    });


    if (
        sectionId === "packets"
    ) {

        loadPackets();

    }


    if (
        sectionId === "statistics"
    ) {

        loadStatistics();

    }

}


/* SYSTEM */

async function loadSystem() {

    try {

        const response =
            await fetch(
                "/api/system"
            );

        const data =
            await response.json();


        document.getElementById(
            "hostname"
        ).textContent =
            data.hostname;


        document.getElementById(
            "hostInfo"
        ).textContent =
            data.hostname;


        document.getElementById(
            "ipInfo"
        ).textContent =
            data.ip;


        document.getElementById(
            "osInfo"
        ).textContent =
            `${data.os} ${data.os_version}`;


        document.getElementById(
            "systemHostname"
        ).textContent =
            data.hostname;


        document.getElementById(
            "systemIP"
        ).textContent =
            data.ip;


        document.getElementById(
            "systemOS"
        ).textContent =
            `${data.os} ${data.os_version}`;


        document.getElementById(
            "systemMachine"
        ).textContent =
            data.machine;


        document.getElementById(
            "systemPython"
        ).textContent =
            data.python;


    } catch (error) {

        console.error(
            "System information error:",
            error
        );

    }

}


/* CAPTURE */

async function startCapture() {

    const button =
        document.getElementById(
            "startButton"
        );


    button.disabled = true;


    try {

        const response =
            await fetch(
                "/api/start",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                "Unable to start capture:\n\n" +
                data.message
            );

        }


        updateStatus();

    } catch (error) {

        alert(
            "Backend connection error."
        );

        console.error(error);

    }

}


async function stopCapture() {

    const button =
        document.getElementById(
            "stopButton"
        );


    button.disabled = true;


    try {

        const response =
            await fetch(
                "/api/stop",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message
            );

        }


        updateStatus();

    } catch (error) {

        console.error(error);

    }

}


/* STATUS */

async function updateStatus() {

    try {

        const response =
            await fetch(
                "/api/status"
            );


        const data =
            await response.json();


        const statusBadge =
            document.getElementById(
                "statusBadge"
            );


        const startButton =
            document.getElementById(
                "startButton"
            );


        const stopButton =
            document.getElementById(
                "stopButton"
            );


        const connectionText =
            document.getElementById(
                "connectionText"
            );


        if (data.running) {

            statusBadge.textContent =
                "CAPTURING";

            statusBadge.classList.add(
                "running"
            );

            startButton.disabled = true;

            stopButton.disabled = false;

            connectionText.textContent =
                "Capturing";


            document
                .getElementById(
                    "liveDot"
                )
                .style.opacity = "1";


        } else {

            statusBadge.textContent =
                "IDLE";

            statusBadge.classList.remove(
                "running"
            );

            startButton.disabled = false;

            stopButton.disabled = true;

            connectionText.textContent =
                "Ready";

            document
                .getElementById(
                    "liveDot"
                )
                .style.opacity = "0.35";

        }


        document.getElementById(
            "captureTime"
        ).textContent =
            formatDuration(
                data.duration
            );


    } catch (error) {

        console.error(
            "Status error:",
            error
        );

    }

}


/* PACKETS */

async function loadPackets() {

    try {

        const response =
            await fetch(
                "/api/packets?limit=200"
            );


        allPackets =
            await response.json();


        renderDashboardPackets(
            allPackets
        );


        renderExplorerPackets(
            allPackets
        );


    } catch (error) {

        console.error(
            "Packet loading error:",
            error
        );

    }

}


function renderDashboardPackets(
    packets
) {

    const table =
        document.getElementById(
            "packetTable"
        );


    if (!packets.length) {

        table.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    No packets captured yet.
                </td>
            </tr>
        `;

        return;

    }


    const display =
        packets.slice(
            0,
            80
        );


    table.innerHTML =
        display
            .map(packet => {

                return `
                    <tr
                        onclick="showPacket(${packet.id})"
                        style="cursor:pointer"
                    >

                        <td>${packet.id}</td>

                        <td>
                            ${packet.timestamp}
                        </td>

                        <td>
                            <span class="protocol">
                                ${escapeHTML(
                                    packet.protocol
                                )}
                            </span>
                        </td>

                        <td>
                            ${escapeHTML(
                                packet.source_ip || "-"
                            )}
                            ${
                                packet.source_port
                                    ? ":" +
                                      packet.source_port
                                    : ""
                            }
                        </td>

                        <td>
                            ${escapeHTML(
                                packet.destination_ip || "-"
                            )}
                            ${
                                packet.destination_port
                                    ? ":" +
                                      packet.destination_port
                                    : ""
                            }
                        </td>

                        <td>
                            ${formatBytes(
                                packet.packet_length
                            )}
                        </td>

                    </tr>
                `;

            })
            .join("");

}


function renderExplorerPackets(
    packets
) {

    const table =
        document.getElementById(
            "explorerTable"
        );


    if (!packets.length) {

        table.innerHTML = `
            <tr>
                <td colspan="8" class="empty">
                    No packets captured yet.
                </td>
            </tr>
        `;

        return;

    }


    table.innerHTML =
        packets
            .map(packet => {

                return `
                    <tr>

                        <td>${packet.id}</td>

                        <td>
                            ${packet.timestamp}
                        </td>

                        <td>
                            <span class="protocol">
                                ${escapeHTML(
                                    packet.protocol
                                )}
                            </span>
                        </td>

                        <td>
                            ${escapeHTML(
                                packet.source_ip || "-"
                            )}
                        </td>

                        <td>
                            ${escapeHTML(
                                packet.destination_ip || "-"
                            )}
                        </td>

                        <td>
                            ${
                                packet.destination_port ||
                                packet.source_port ||
                                "-"
                            }
                        </td>

                        <td>
                            ${formatBytes(
                                packet.packet_length
                            )}
                        </td>

                        <td>

                            <button
                                class="btn btn-secondary"
                                onclick="showPacket(${packet.id})"
                            >
                                View
                            </button>

                        </td>

                    </tr>
                `;

            })
            .join("");

}


/* PACKET DETAILS */

async function showPacket(
    packetId
) {

    try {

        const response =
            await fetch(
                `/api/packet/${packetId}`
            );


        const packet =
            await response.json();


        const details =
            document.getElementById(
                "packetDetails"
            );


        const fields = [

            [
                "Packet ID",
                packet.id
            ],

            [
                "Timestamp",
                packet.timestamp
            ],

            [
                "Protocol",
                packet.protocol
            ],

            [
                "Source IP",
                packet.source_ip || "-"
            ],

            [
                "Destination IP",
                packet.destination_ip || "-"
            ],

            [
                "Source Port",
                packet.source_port || "-"
            ],

            [
                "Destination Port",
                packet.destination_port || "-"
            ],

            [
                "Packet Length",
                formatBytes(
                    packet.packet_length
                )
            ],

            [
                "TCP Flags",
                packet.tcp_flags || "-"
            ],

            [
                "Information",
                packet.info || "-"
            ]

        ];


        details.innerHTML =
            fields
                .map(field => {

                    return `
                        <div class="detail">

                            <div class="detail-label">
                                ${escapeHTML(
                                    field[0]
                                )}
                            </div>

                            <div class="detail-value">
                                ${escapeHTML(
                                    String(
                                        field[1]
                                    )
                                )}
                            </div>

                        </div>
                    `;

                })
                .join("");


        document
            .getElementById(
                "packetModal"
            )
            .classList.add(
                "show"
            );


    } catch (error) {

        console.error(
            "Packet details error:",
            error
        );

    }

}


function closeModal() {

    document
        .getElementById(
            "packetModal"
        )
        .classList.remove(
            "show"
        );

}


/* STATISTICS */

async function loadStatistics() {

    try {

        const response =
            await fetch(
                "/api/statistics"
            );


        const data =
            await response.json();


        document.getElementById(
            "totalPackets"
        ).textContent =
            data.total.toLocaleString();


        document.getElementById(
            "tcpPackets"
        ).textContent =
            data.tcp.toLocaleString();


        document.getElementById(
            "udpPackets"
        ).textContent =
            data.udp.toLocaleString();


        document.getElementById(
            "icmpPackets"
        ).textContent =
            data.icmp.toLocaleString();


        document.getElementById(
            "dnsPackets"
        ).textContent =
            data.dns.toLocaleString();


        document.getElementById(
            "webPackets"
        ).textContent =
            (
                data.http +
                data.https
            ).toLocaleString();


        document.getElementById(
            "totalBytes"
        ).textContent =
            formatBytes(
                data.bytes
            );


        renderProtocolChart(
            data.protocols
        );


    } catch (error) {

        console.error(
            "Statistics error:",
            error
        );

    }

}


function renderProtocolChart(
    protocols
) {

    const container =
        document.getElementById(
            "protocolChart"
        );


    const statisticContainer =
        document.getElementById(
            "statisticsChart"
        );


    const entries =
        Object.entries(
            protocols
        );


    if (!entries.length) {

        container.innerHTML = `
            <div class="chart-empty">
                Waiting for packets...
            </div>
        `;

        statisticContainer.innerHTML = `
            <div class="chart-empty">
                No traffic statistics available.
            </div>
        `;

        return;

    }


    const maximum =
        Math.max(
            ...entries.map(
                item => item[1]
            )
        );


    const html =
        entries
            .map(item => {

                const protocol =
                    item[0];

                const count =
                    item[1];

                const percentage =
                    maximum > 0
                        ? (
                            count /
                            maximum
                        ) * 100
                        : 0;


                return `
                    <div class="chart-row">

                        <div class="chart-label">

                            <span>
                                ${escapeHTML(
                                    protocol
                                )}
                            </span>

                            <strong>
                                ${count.toLocaleString()}
                            </strong>

                        </div>

                        <div class="chart-track">

                            <div
                                class="chart-bar"
                                style="width:${percentage}%"
                            ></div>

                        </div>

                    </div>
                `;

            })
            .join("");


    container.innerHTML =
        html;


    statisticContainer.innerHTML =
        html;

}


/* SEARCH */

function filterPackets() {

    const search =
        document
            .getElementById(
                "packetSearch"
            )
            .value
            .toLowerCase()
            .trim();


    if (!search) {

        renderExplorerPackets(
            allPackets
        );

        return;

    }


    const filtered =
        allPackets.filter(
            packet => {

                const content =
                    [
                        packet.id,
                        packet.protocol,
                        packet.source_ip,
                        packet.destination_ip,
                        packet.source_port,
                        packet.destination_port,
                        packet.info
                    ]
                    .join(" ")
                    .toLowerCase();


                return content.includes(
                    search
                );

            }
        );


    renderExplorerPackets(
        filtered
    );

}


/* CLEAR */

async function clearPackets() {

    const confirmed =
        confirm(
            "Clear all captured packet data?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/clear",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                data.message
            );

            return;

        }


        allPackets = [];

        loadPackets();

        loadStatistics();


    } catch (error) {

        alert(
            "Unable to clear packet data."
        );

    }

}


/* EXPORT */

async function exportPackets() {

    try {

        const response =
            await fetch(
                "/api/export"
            );


        const data =
            await response.json();


        if (!data.success) {

            alert(
                "Export failed."
            );

            return;

        }


        const link =
            document.createElement(
                "a"
            );


        link.href =
            data.url;

        link.download =
            data.filename;

        document.body.appendChild(
            link
        );

        link.click();

        link.remove();


    } catch (error) {

        alert(
            "Unable to export packet data."
        );

    }

}


/* REFRESH */

function startRefreshing() {

    updateStatus();

    loadPackets();

    loadStatistics();


    if (refreshTimer) {

        clearInterval(
            refreshTimer
        );

    }


    refreshTimer =
        setInterval(
            () => {

                updateStatus();

                loadPackets();

                loadStatistics();

            },
            1500
        );

}


/* HELPERS */

function formatBytes(
    bytes
) {

    if (
        bytes === null ||
        bytes === undefined
    ) {

        return "0 B";

    }


    if (bytes < 1024) {

        return `${bytes} B`;

    }


    if (bytes < 1024 * 1024) {

        return (
            `${(
                bytes /
                1024
            ).toFixed(1)} KB`
        );

    }


    return (
        `${(
            bytes /
            (1024 * 1024)
        ).toFixed(1)} MB`
    );

}


function formatDuration(
    seconds
) {

    seconds =
        Math.floor(
            seconds || 0
        );


    const minutes =
        Math.floor(
            seconds / 60
        );


    const remaining =
        seconds % 60;


    if (minutes > 0) {

        return `${minutes}m ${remaining}s`;

    }


    return `${remaining}s`;

}


function escapeHTML(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape"
        ) {

            closeModal();

        }

    }
);