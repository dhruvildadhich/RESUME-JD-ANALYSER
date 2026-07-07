import React from "react";
import { COLORS, RADIUS, SPACING } from "../../styles/designTokens";

function SkeletonBar({ width = "100%", height = 14 }) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius: RADIUS.sm,
        backgroundColor: COLORS["surface-2"],
        animation: "pulse 2s ease-in-out infinite",
      }}
    />
  );
}

function SkeletonBlock({ width = "100%", height = 80, radius = RADIUS.xl }) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius: radius,
        backgroundColor: COLORS["surface-2"],
        animation: "pulse 2s ease-in-out infinite",
      }}
    />
  );
}

export function Skeleton({ children, className = "" }) {
  return <div className={className} style={{ display: "flex", flexDirection: "column", gap: SPACING.sm }}>{children}</div>;
}

Skeleton.Bar = SkeletonBar;
Skeleton.Block = SkeletonBlock;

export default function LoadingState({ type = "results" }) {
  const sharedPulse = { animation: "pulse 2s ease-in-out infinite" };

  if (type === "card") {
    return (
      <div style={{ backgroundColor: COLORS["surface-1"], borderRadius: RADIUS.xl, padding: SPACING.xl, display: "flex", flexDirection: "column", gap: SPACING.md, ...sharedPulse }}>
        <SkeletonBar width="120px" />
        <SkeletonBlock height={60} radius={RADIUS.md} />
        <SkeletonBar width="80%" />
        <SkeletonBar width="60%" />
      </div>
    );
  }

  if (type === "dashboard") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: SPACING.xl }}>
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_2fr] gap-[30px]">
          <div style={{ backgroundColor: COLORS["surface-1"], borderRadius: RADIUS.xl, padding: SPACING.xxl, display: "flex", flexDirection: "column", alignItems: "center", gap: SPACING.md }}>
            <SkeletonBar width="100px" />
            <SkeletonBlock width={160} height={160} radius="50%" />
            <SkeletonBar width="120px" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-[15px]">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} style={{ backgroundColor: COLORS["surface-1"], borderRadius: RADIUS.xl, padding: SPACING.lg, display: "flex", flexDirection: "column", gap: SPACING.sm }}>
                <SkeletonBar width="80px" />
                <SkeletonBar width="50px" height={28} />
                <SkeletonBar width="100px" />
              </div>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-[30px]">
          {[1, 2].map((i) => (
            <div key={i} style={{ backgroundColor: COLORS["surface-1"], borderRadius: RADIUS.xl, padding: SPACING.xl, display: "flex", flexDirection: "column", gap: SPACING.md }}>
              <SkeletonBar width="100px" />
              <SkeletonBar width="60%" height={18} />
              <SkeletonBar width="40%" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return null;
}
