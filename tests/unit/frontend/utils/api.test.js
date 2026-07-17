import { API } from "../../../../frontend/src/constants.js";
import {
  record,
  refreshDevices,
  startLive,
  stopLive,
} from "../../../../frontend/src/utils/api.js";

describe("api utils", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("refreshDevices requests devices list", async () => {
    const payload = [{ id: "cam-1" }];
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      json: async () => payload,
    });

    const result = await refreshDevices();

    expect(fetchMock).toHaveBeenCalledWith(`${API}/devices`);
    expect(result).toEqual(payload);
  });

  it("record sends remote command with duration", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({});

    await record("cam-22", 12);

    expect(fetchMock).toHaveBeenCalledWith(`${API}/devices/cam-22/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "record", seconds: 12 }),
    });
  });

  it("startLive throws when backend returns non-ok", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({ ok: false });

    await expect(startLive("cam-err")).rejects.toThrow(
      "Failed to start live for device cam-err",
    );
  });

  it("stopLive returns parsed backend response on success", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    });

    await expect(stopLive("cam-3")).resolves.toEqual({ ok: true });
  });
});
