import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import DeviceCard from "../../../../frontend/src/components/DeviceCard.jsx";
import {
  record,
  snapshot,
  startLive,
  stopLive,
} from "../../../../frontend/src/utils/api.js";

vi.mock("../../../../frontend/src/utils/api.js", () => ({
  snapshot: vi.fn(),
  record: vi.fn(),
  startLive: vi.fn(),
  stopLive: vi.fn(),
}));

function onlineDevice(overrides = {}) {
  return {
    id: "dev-1",
    name: "Front Camera",
    last_seen: new Date().toISOString(),
    ...overrides,
  };
}

describe("DeviceCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends snapshot and record actions", () => {
    render(<DeviceCard device={onlineDevice()} />);

    fireEvent.click(screen.getByRole("button", { name: /snapshot/i }));
    expect(snapshot).toHaveBeenCalledWith("dev-1");

    fireEvent.change(screen.getByRole("spinbutton"), {
      target: { value: "14" },
    });
    fireEvent.click(screen.getByRole("button", { name: /record/i }));
    expect(record).toHaveBeenCalledWith("dev-1", 14);
  });

  it("disables live button when device is offline", () => {
    render(<DeviceCard device={onlineDevice({ last_seen: null })} />);
    expect(screen.getByRole("button", { name: /live/i })).toBeDisabled();
  });

  it("starts and stops live mode and renders live iframe", async () => {
    startLive.mockResolvedValue({ ok: true });
    stopLive.mockResolvedValue({ ok: true });

    render(<DeviceCard device={onlineDevice()} />);

    fireEvent.click(screen.getByRole("button", { name: /live/i }));
    await waitFor(() => expect(startLive).toHaveBeenCalledWith("dev-1"));
    expect(
      screen.getByTitle("Live stream dev-1", { exact: false }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /stop/i }));
    await waitFor(() => expect(stopLive).toHaveBeenCalledWith("dev-1"));
  });

  it("shows media viewing link when upload url exists", () => {
    render(
      <DeviceCard
        device={onlineDevice()}
        lastUploadUrl="http://localhost:8000/uploads/video.mp4"
      />,
    );

    expect(screen.getByRole("link", { name: /open last upload/i })).toHaveAttribute(
      "href",
      "http://localhost:8000/uploads/video.mp4",
    );
  });
});
