import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import api from "../../services/api";

const verdictStyles = {
  SUPPORTS: "bg-emerald-100 text-emerald-700",
  REFUTES: "bg-red-100 text-red-700",
  NEI: "bg-amber-100 text-amber-700",
};

const verdictLabels = {
  SUPPORTS: "Supported",
  REFUTES: "Refuted",
  NEI: "Not enough information",
};

const mergeHistory = (previous, incoming) => {
  const byId = new Map();

  [...previous, ...incoming].forEach((item) => {
    if (!item) {
      return;
    }

    byId.set(item.id, item);
  });

  return Array.from(byId.values());
};

const getErrorMessage = (err) =>
  err?.response?.data?.detail ||
  err?.message ||
  "Could not load your verification history.";

export default function HistorySection() {
  const pageSize = 20;
  const [history, setHistory] = useState([]);
  const [counters, setCounters] = useState(null);
  const [filter, setFilter] = useState("ALL");
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasNext, setHasNext] = useState(true);
  const [nextPage, setNextPage] = useState(1);
  const [error, setError] = useState("");
  const [loadMoreError, setLoadMoreError] = useState("");
  const loaderRef = useRef(null);
  const loadedPagesRef = useRef(new Set());
  const inFlightPageRef = useRef(null);

  const applyHistoryPage = useCallback((page, payload, { replace = false } = {}) => {
    const results = Array.isArray(payload?.results) ? payload.results : [];

    setHistory((previous) => (replace ? results : mergeHistory(previous, results)));
    loadedPagesRef.current.add(page);
    setHasNext(Boolean(payload?.has_next));
    setNextPage(payload?.next_page ?? null);
  }, []);

  const fetchCounters = useCallback(async () => {
    const response = await api.get("/history/counter/");
    setCounters(response.data);
  }, []);

  const fetchHistoryPage = useCallback(async (page, { replace = false, force = false } = {}) => {
    if (!force && (inFlightPageRef.current === page || loadedPagesRef.current.has(page))) {
      return;
    }

    if (!force && !hasNext && page !== 1) {
      return;
    }

    inFlightPageRef.current = page;

    if (page === 1) {
      setLoadingInitial(true);
      setError("");
    } else {
      setLoadingMore(true);
      setLoadMoreError("");
    }

    try {
      const response = await api.get("/history/", {
        params: { page, limit: pageSize },
      });

      applyHistoryPage(page, response.data, { replace });
    } catch (err) {
      const message = getErrorMessage(err);
      if (page === 1) {
        setError(message);
      } else {
        setLoadMoreError(message);
      }
    } finally {
      inFlightPageRef.current = null;
      setLoadingInitial(false);
      setLoadingMore(false);
    }
  }, [applyHistoryPage, hasNext, loadingInitial, pageSize]);

  const allFilteredHistory = useMemo(() => {
    return filter === "ALL"
      ? history
      : history.filter((item) => item.verdict === filter);
  }, [filter, history]);

  useEffect(() => {
    let active = true;

    const loadInitialHistory = async () => {
      loadedPagesRef.current = new Set();
      inFlightPageRef.current = null;
      setHistory([]);
      setCounters(null);
      setError("");
      setLoadMoreError("");
      setHasNext(true);
      setNextPage(1);
      setLoadingInitial(true);

      const [historyResult, counterResult] = await Promise.allSettled([
        api.get("/history/", { params: { page: 1, limit: pageSize } }),
        fetchCounters(),
      ]);

      if (!active) {
        return;
      }

      if (historyResult.status === "fulfilled") {
        applyHistoryPage(1, historyResult.value.data, { replace: true });
      } else {
        setError(getErrorMessage(historyResult.reason));
      }

      if (counterResult.status === "rejected") {
        setCounters(null);
      }

      setLoadingInitial(false);
    };

    loadInitialHistory();

    return () => {
      active = false;
    };
  }, [applyHistoryPage, fetchCounters, pageSize]);

  useEffect(() => {
    if (!loaderRef.current) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (
          entries[0].isIntersecting &&
          hasNext &&
          !loadingMore &&
          !loadingInitial &&
          !loadMoreError &&
          nextPage
        ) {
          fetchHistoryPage(nextPage);
        }
      },
      {
        root: null,
        rootMargin: "200px",
        threshold: 0,
      }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => observer.disconnect();
  }, [allFilteredHistory.length, fetchHistoryPage, hasNext, loadingMore, loadingInitial, loadMoreError, nextPage]);

  if (loadingInitial && history.length === 0 && !error) {
    return (
      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3 text-gray-500">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-indigo-600" />
          <p>Loading verification history...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-2xl bg-white p-6 shadow-sm">
        <p className="text-red-600">{error}</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm font-medium text-indigo-600">Your activity</p>
        <h2 className="text-2xl font-bold text-gray-900">
          Verification history
        </h2>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Total checks" value={counters?.total ?? 0} />
        <StatCard
          label="Supported"
          value={counters?.supports ?? 0}
          accent="text-emerald-600"
        />
        <StatCard
          label="Refuted"
          value={counters?.refutes ?? 0}
          accent="text-red-600"
        />
        <StatCard
          label="Needs evidence"
          value={counters?.not_enough_information ?? 0}
          accent="text-amber-600"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {[
          ["ALL", "All"],
          ["SUPPORTS", "Supported"],
          ["REFUTES", "Refuted"],
          ["NEI", "Needs evidence"],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`rounded-full px-4 py-2 text-sm font-medium transition ${
              filter === value
                ? "bg-indigo-600 text-white"
                : "bg-white text-gray-600 shadow-sm hover:bg-gray-50"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {allFilteredHistory.length === 0 && !hasNext && !loadMoreError ? (
          <div className="rounded-2xl bg-white p-8 text-center shadow-sm">
            <p className="text-gray-500">No verification history found.</p>
          </div>
        ) : (
          allFilteredHistory.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="space-y-2">
                  <p className="text-base font-semibold text-gray-900">
                    {item.claim_text}
                  </p>

                  <div className="flex flex-wrap items-center gap-2">
                    {item.image_indicator && (
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-700">
                        {item.image_indicator} OCR
                      </span>
                    )}

                    {item.normalized_claim && (
                      <span className="rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-indigo-700">
                        Normalized claim available
                      </span>
                    )}
                  </div>

                  {item.explanation && (
                    <p className="text-sm leading-6 text-gray-600">
                      {item.explanation}
                    </p>
                  )}

                  {item.normalized_claim && (
                    <p className="text-sm leading-6 text-gray-500">
                      <span className="font-semibold text-gray-700">Normalized:</span>{" "}
                      {item.normalized_claim}
                    </p>
                  )}

                  <p className="text-xs text-gray-400">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>

                <div className="flex shrink-0 flex-wrap items-center gap-2">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      verdictStyles[item.verdict] || "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {verdictLabels[item.verdict] || item.status}
                  </span>

                  {item.confidence_score !== null &&
                    item.confidence_score !== undefined && (
                      <span className="text-sm font-semibold text-gray-700">
                        {Math.round(item.confidence_score * 100)}% confident
                      </span>
                    )}

                  {item.credibility_score !== null &&
                    item.credibility_score !== undefined && (
                      <span className="text-sm font-semibold text-gray-700">
                        {Math.round(item.credibility_score * 100)}% credible
                      </span>
                    )}
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {loadMoreError && (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <div className="flex items-center justify-between gap-4">
            <span>{loadMoreError}</span>
            <button
              type="button"
              onClick={() => fetchHistoryPage(nextPage, { force: true })}
              className="rounded-full bg-red-600 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-white transition hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {(hasNext || loadingMore) && !loadMoreError && (
        <div ref={loaderRef} className="flex justify-center py-6">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            {loadingMore && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-indigo-600" />
            )}
            <span>{loadingMore ? "Loading more..." : "Scroll to load more"}</span>
          </div>
        </div>
      )}
    </section>
  );
}

function StatCard({ label, value, accent = "text-gray-900" }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${accent}`}>{value}</p>
    </div>
  );
}
