# PAIML-POLE-ANALYST-046 — DTOs for multi-frame pose response

## Meta
- **Project:** pole_analyst
- **Phase:** 14 — Stitch Design: Pose Gallery + Metric Detail Modal
- **Status:** TODO
- **Blocks:** PAIML-POLE-ANALYST-047
- **Blocked By:** — (none)

## Description

Create TypeScript DTO models for the multi-frame pose response endpoint
(`GET /api/analysis/videos/{video_id}/pose/frames`). The current `PoseFrame` interface
in `features/analysis/models/pose.ts` only supports a single frame.

### New interfaces

```typescript
/** Single pose frame from the gallery endpoint. */
export interface PoseFrameItem {
  frame_number: number;
  frame_image_path: string;
  phase: string;         // "init" | "execution" | "exit"
  metric: string;
  z_score: number;
  issues: PoseIssue[];
}

/** Multi-frame pose gallery response. */
export interface PoseFrameGallery {
  frames: PoseFrameItem[];
  total_frames: number;
}
```

### Tasks
- [ ] Add `PoseFrameItem` and `PoseFrameGallery` interfaces to `features/analysis/models/pose.ts`.
- [ ] Add unit tests for the interfaces.
- [ ] Ensure the interfaces match the backend response shape from PAIML-POLE-API-057.

### Acceptance Criteria
- [ ] New interfaces exist and match the backend contract.
- [ ] Unit tests pass.
