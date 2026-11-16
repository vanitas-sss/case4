const P = {
    overview: (
        <>
            <rect x="4" y="4" width="6.5" height="6.5" rx="1.5" />
            <rect x="13.5" y="4" width="6.5" height="6.5" rx="1.5" />
            <rect x="4" y="13.5" width="6.5" height="6.5" rx="1.5" />
            <rect x="13.5" y="13.5" width="6.5" height="6.5" rx="1.5" />
        </>
    ),
    servers: (
        <>
            <rect x="3.5" y="4" width="17" height="6.5" rx="2" />
            <rect x="3.5" y="13.5" width="17" height="6.5" rx="2" />
            <path d="M7 7.25h.01M7 16.75h.01" />
        </>
    ),
    containers: (
        <>
            <path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z" />
            <path d="M12 12l8-4.5M12 12L4 7.5M12 12v9" />
        </>
    ),
    metrics: <path d="M3.5 19.5h17M5 16l4.5-5 3.5 3 6-7" />,
    clock: (
        <>
            <circle cx="12" cy="12" r="8.5" />
            <path d="M12 7v5l3 2" />
        </>
    ),
    db: (
        <>
            <ellipse cx="12" cy="6" rx="7" ry="2.8" />
            <path d="M5 6v6c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6M5 12v6c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-6" />
        </>
    ),
    book: (
        <>
            <path d="M6 3.5h11a1.5 1.5 0 011.5 1.5v14a1.5 1.5 0 01-1.5 1.5H6a1.5 1.5 0 01-1.5-1.5V5A1.5 1.5 0 016 3.5z" />
            <path d="M9 3.5v17M12 8h3.5" />
        </>
    ),
    bell: (
        <>
            <path d="M6 16V11a6 6 0 1112 0v5l1.5 2h-15L6 16z" />
            <path d="M10 21h4" />
        </>
    ),
    search: (
        <>
            <circle cx="11" cy="11" r="6.5" />
            <path d="M16 16l4 4" />
        </>
    ),
    close: <path d="M6 6l12 12M18 6L6 18" />,
    check: <path d="M5 12.5l4.5 4.5L19 7.5" />,
    arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
    plus: <path d="M12 5v14M5 12h14" />,
}
export default function Icon({ name, size = 20 }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            {P[name]}
        </svg>
    )
}
