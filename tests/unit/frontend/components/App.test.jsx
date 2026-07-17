import { render, screen, waitFor } from "@testing-library/react";

import App from "../../../../frontend/src/App.jsx";
import { refreshDevices } from "../../../../frontend/src/utils/api.js";

vi.mock("../../../../frontend/src/utils/api.js", () => ({
  refreshDevices: vi.fn(),
}));

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads devices and shows online count", async () => {
    refreshDevices.mockResolvedValue([
      { id: "cam-1", name: "Front", last_seen: new Date().toISOString() },
      { id: "cam-2", name: "Back", last_seen: null },
    ]);

    render(<App />);

    await waitFor(() => expect(refreshDevices).toHaveBeenCalled());
    expect(screen.getByText("2 devices registered")).toBeInTheDocument();
    expect(screen.getByText("1 online")).toBeInTheDocument();
    expect(screen.getByText("Front")).toBeInTheDocument();
    expect(screen.getByText("Back")).toBeInTheDocument();
  });

  it("shows empty state when no devices are returned", async () => {
    refreshDevices.mockResolvedValue([]);

    render(<App />);

    await waitFor(() => expect(screen.getByText("No devices found")).toBeInTheDocument());
    expect(screen.getByText("Waiting for cameras to connect…")).toBeInTheDocument();
  });
});
