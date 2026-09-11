// The store lines against recorded fixtures — no live portal, no key, no network.
//
//   npx -y tsx tests/tracks.test.ts
//
// Each parser is fed the recorded shape of the endpoint it reads and the seed
// row it builds is asserted against the words of 043-the-beacons.sql.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

import {
  BEACON_STATUSES,
  playStatus,
  STORE_CHANNELS,
  type ReportRow,
  type TrackRow,
} from "../src/lines/tracks.js";
import {
  parsePlayReleases,
  parsePlayReviews,
  playReadTracksByRelease,
  playReportRows,
  playTrackRow,
  playUnheld,
  releaseState,
  PLAY_REACH,
  PLAY_TRACK_IDS,
  type PlayTrack,
} from "../src/lines/play.js";
import {
  galaxyReportRows,
  galaxyTrackRow,
  parseGalaxyApp,
  parseGalaxyApps,
  parseGalaxyBeta,
  parseGalaxyComments,
} from "../src/lines/galaxy.js";
import {
  microsoftReportRows,
  microsoftTrackRow,
  parseMsApps,
  parseMsFlights,
  parseMsReviews,
  parseMsSubmission,
  parseMsSubmissionStatus,
} from "../src/lines/microsoft.js";
import { androidPackage, mergeReports } from "../src/census/tracks_census.js";

const FIXTURES = path.join(fileURLToPath(new URL(".", import.meta.url)), "fixtures");

function fixture(store: string, name: string): any {
  return JSON.parse(readFileSync(path.join(FIXTURES, store, `${name}.json`), "utf8"));
}

let checked = 0;
const failures: string[] = [];

function is(what: string, got: unknown, want: unknown) {
  checked += 1;
  const a = JSON.stringify(got);
  const b = JSON.stringify(want);
  if (a !== b) failures.push(`${what}\n    got  ${a}\n    want ${b}`);
}

function ok(what: string, truth: boolean) {
  checked += 1;
  if (!truth) failures.push(what);
}

// Every seed row speaks the register's own words.
function lawful(what: string, row: TrackRow) {
  ok(`${what}: channel is a register channel`, (STORE_CHANNELS as readonly string[]).includes(row.channel));
  ok(
    `${what}: status is a 043 word or null`,
    row.status === null || (BEACON_STATUSES as readonly string[]).includes(row.status)
  );
  ok(`${what}: app_id is not empty`, row.app_id.trim() !== "");
  ok(`${what}: note is a string`, typeof row.note === "string");
}

function reportLawful(what: string, rows: ReportRow[]) {
  for (const row of rows) {
    ok(`${what}: id names its source`, /^(discord|play|galaxy|microsoft):.+$/.test(row.id));
    ok(`${what}: kind is a seed kind`, ["bug", "note", "review"].includes(row.kind));
    ok(`${what}: text is whole`, row.text.trim() !== "");
    ok(`${what}: said_by carries a name`, row.said_by.trim() !== "");
  }
}

// ── Google Play ────────────────────────────────────────────────────────────

const playBeta = parsePlayReleases(fixture("play", "releases-list"));
is("play release lifecycles", playBeta.map((r) => r.lifecycle), [
  "RELEASE_LIFECYCLE_STATE_IN_REVIEW",
  "RELEASE_LIFECYCLE_STATE_PUBLISHED",
]);
is("play release names", playBeta.map((r) => r.name), ["1.5.0-beta", "1.4.1"]);
is("play release version codes", playBeta[0].version_codes, ["13"]);
is("a ReleaseSummary names the track it sits on", playBeta[0].track, "beta");

// One case per releaseLifecycleState the discovery document names, and one for a
// release Play sent no lifecycle state with.
const LIFECYCLES: ReadonlyArray<readonly [string | null, string | null]> = [
  ["RELEASE_LIFECYCLE_STATE_UNSPECIFIED", null],
  ["RELEASE_LIFECYCLE_STATE_DRAFT", "draft"],
  ["RELEASE_LIFECYCLE_STATE_NOT_SENT_FOR_REVIEW", "draft"],
  ["RELEASE_LIFECYCLE_STATE_IN_REVIEW", "inProgress"],
  ["RELEASE_LIFECYCLE_STATE_APPROVED_NOT_PUBLISHED", "inProgress"],
  ["RELEASE_LIFECYCLE_STATE_NOT_APPROVED", "rejected"],
  ["RELEASE_LIFECYCLE_STATE_PUBLISHED", "completed"],
  [null, null],
];
for (const [lifecycle, state] of LIFECYCLES) {
  is(
    `the release word for ${lifecycle ?? "a release Play named no lifecycle state for"}`,
    releaseState({ track: null, name: null, lifecycle, version_codes: [] }),
    state
  );
}

is(
  "a standing release reads by the track it stands on",
  ["qa", "internal", "alpha", "beta", "production", "open-beta"].map((t) =>
    playStatus(t, "completed")
  ),
  ["internal_testing", "internal_testing", "closed_testing", "open_testing", "published", "closed_testing"]
);
is(
  "a track id alone names no status",
  ["qa", "alpha", "beta", "production"].map((t) => playStatus(t, null)),
  [null, null, null, null]
);
is(
  "a release in review is in review on any track",
  ["qa", "alpha", "beta", "production"].map((t) => playStatus(t, "inProgress")),
  ["in_review", "in_review", "in_review", "in_review"]
);
is(
  "a refused release is refused on any track",
  ["alpha", "beta", "production"].map((t) => playStatus(t, "rejected")),
  ["rejected", "rejected", "rejected"]
);
is(
  "a draft is planned on any track",
  ["alpha", "beta", "production"].map((t) => playStatus(t, "draft")),
  ["planned", "planned", "planned"]
);

// The ReleaseSummary the discovery document draws: a published production release
// with one active artifact and no release name.
const discovery = parsePlayReleases({
  releases: [
    {
      track: "production",
      releaseLifecycleState: "RELEASE_LIFECYCLE_STATE_PUBLISHED",
      activeArtifacts: [{ versionCode: 13 }],
    },
  ],
});
const discoveryRow = playTrackRow(
  "resonance-echoes",
  "com.audhd.resonance-echoes",
  [{ track: "production", releases: discovery }],
  null
);
lawful("play row from the discovery shape", discoveryRow);
is("a published production release reads as published", discoveryRow.status, "published");
is(
  "a release Play wrote no name for stands under its version code",
  discoveryRow.published_version,
  "13"
);

const unnamedRow = playTrackRow(
  "resonance-echoes",
  "com.audhd.resonance-echoes",
  [{ track: "beta", releases: [{ track: "beta", name: "1.6.0-beta", lifecycle: null, version_codes: ["16"] }] }],
  null
);
is("a release with no lifecycle state leaves the status unwritten", unnamedRow.status, null);

is(
  "the reach holds every 043 word once",
  [...PLAY_REACH].sort(),
  [...BEACON_STATUSES].sort()
);
ok(
  "qa and production are on the track road",
  PLAY_TRACK_IDS.includes("qa") && PLAY_TRACK_IDS.includes("production")
);

is(
  "the Tauri identifier's hyphens become the Android package's underscores",
  androidPackage("com.audhd.resonance-echoes"),
  "com.audhd.resonance_echoes"
);
is(
  "an identifier with no hyphen is its own package",
  androidPackage("com.audhd.resonanceechoes"),
  "com.audhd.resonanceechoes"
);

// ── The track road, against a stubbed portal ───────────────────────────────

// Every request is answered from the fixtures; a track with no fixture answers
// 404, and an address off the androidpublisher root throws.
function stubPlay(served: Record<string, unknown>): () => void {
  const held = globalThis.fetch;
  globalThis.fetch = (async (input: unknown) => {
    const url = String(input);
    if (!url.startsWith("https://androidpublisher.googleapis.com/")) {
      throw new Error(`the proof reached off the stub: ${url}`);
    }
    const track = /\/tracks\/([^/]+)\/releases/.exec(url)?.[1] ?? "";
    const body = served[track];
    if (body === undefined) return new Response("", { status: 404 });
    return new Response(JSON.stringify(body), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  }) as typeof fetch;
  return () => {
    globalThis.fetch = held;
  };
}

const unstubBeta = stubPlay({ beta: fixture("play", "releases-list") });
const road = await playReadTracksByRelease("no-token", "com.audhd.resonance-echoes");
const oneTrack = await playReadTracksByRelease("no-token", "com.audhd.resonance-echoes", ["beta"]);
unstubBeta();
is("the road reads the track that answered", road.answered, ["beta"]);
is("the road names every track that answered 404", road.unanswered, [
  "qa",
  "internal",
  "alpha",
  "production",
]);
is("the road builds only the track it read", road.tracks.map((t) => t.track), ["beta"]);
is("the road reads the tracks it is named", oneTrack.answered, ["beta"]);
is("the road named one track reads no other", oneTrack.unanswered, []);

const unstubNone = stubPlay({});
const unheld = await playReadTracksByRelease("no-token", "com.audhd.resonance-void");
unstubNone();
is("a package no named track answered for reads no track", unheld.answered, []);
is("a package no named track answered for builds no row", unheld.tracks, []);
is(
  "a package Play answered nothing for is said, never written",
  playUnheld("com.audhd.resonance-void", unheld.unanswered),
  "Google Play answered 404 for every named track of com.audhd.resonance-void — qa, internal, alpha, beta, production. No track was read and no row is written."
);

const unstubWhole = stubPlay({
  qa: fixture("play", "releases-list-qa"),
  beta: fixture("play", "releases-list"),
  production: fixture("play", "releases-list-production"),
});
const whole = await playReadTracksByRelease("no-token", "com.audhd.resonance-echoes");
unstubWhole();
is("the road reads every track that answered", whole.answered, ["qa", "beta", "production"]);

// A 204, or an ok response with an empty or whitespace body, is an empty
// reading: the track is answered, and it carries no releases.
function stubPlayRaw(served: Record<string, { status: number; body: string | null }>): () => void {
  const held = globalThis.fetch;
  globalThis.fetch = (async (input: unknown) => {
    const url = String(input);
    const track = /\/tracks\/([^/]+)\/releases/.exec(url)?.[1] ?? "";
    const answer = served[track];
    if (!answer) return new Response("", { status: 404 });
    return new Response(answer.body, {
      status: answer.status,
      headers: { "content-type": "application/json" },
    });
  }) as typeof fetch;
  return () => {
    globalThis.fetch = held;
  };
}

const unstubEmpty = stubPlayRaw({
  production: { status: 204, body: null },
  beta: { status: 200, body: "   " },
});
const empty = await playReadTracksByRelease("no-token", "com.audhd.resonance-echoes", [
  "production",
  "beta",
]);
unstubEmpty();
is("a 204 track answers with no releases", empty.answered, ["production", "beta"]);
is("an empty reading builds no track row", empty.tracks, []);
is("an empty body parses as no releases", parsePlayReleases({}), []);

const playRow = playTrackRow(
  "resonance-echoes",
  "com.audhd.resonance-echoes",
  whole.tracks,
  "https://play.google.com/apps/testing/com.audhd.resonance-echoes"
);
lawful("play row", playRow);
is("play row status", playRow.status, "published");
is("play row published version", playRow.published_version, "1.3.0");
is("play row testing version", playRow.testing_version, "1.4.1");
is("play row names no tester count", playRow.testers, null);
is(
  "play row listing url",
  playRow.listing_url,
  "https://play.google.com/store/apps/details?id=com.audhd.resonance-echoes"
);
is(
  "play row testing url is the register's own",
  playRow.testing_url,
  "https://play.google.com/apps/testing/com.audhd.resonance-echoes"
);
is(
  "play row note is the lifecycles and the tester lists the bridge does not read",
  playRow.note,
  "qa RELEASE_LIFECYCLE_STATE_PUBLISHED 1.4.1 · beta RELEASE_LIFECYCLE_STATE_IN_REVIEW 1.5.0-beta · production RELEASE_LIFECYCLE_STATE_PUBLISHED 1.3.0 · tester lists are inside an edit; not read by the bridge"
);

const betaRow = playTrackRow(
  "resonance-echoes",
  "com.audhd.resonance-echoes",
  [{ track: "beta", releases: playBeta }],
  null
);
lawful("play row from one track", betaRow);
is("the track road reads the beta track's lifecycle", betaRow.status, "in_review");
is(
  "one track's note speaks its lifecycle and no tester count",
  betaRow.note,
  "beta RELEASE_LIFECYCLE_STATE_IN_REVIEW 1.5.0-beta · tester lists are inside an edit; not read by the bridge"
);

const playRefused: PlayTrack[] = [
  { track: "production", releases: parsePlayReleases(fixture("play", "releases-list-production")) },
  { track: "alpha", releases: parsePlayReleases(fixture("play", "releases-list-not-approved")) },
];
const rejectedRow = playTrackRow("resonance-echoes", "com.audhd.resonance-echoes", playRefused, null);
is("a refused alpha does not unpublish a live app", rejectedRow.status, "published");
is(
  "a refused track alone answers rejected",
  playTrackRow("resonance-echoes", "com.audhd.resonance-echoes", playRefused.slice(1), null).status,
  "rejected"
);
is(
  "a refusal the status word cannot carry reaches the note",
  rejectedRow.note,
  "production RELEASE_LIFECYCLE_STATE_PUBLISHED 1.3.0 · alpha RELEASE_LIFECYCLE_STATE_NOT_APPROVED 1.5.0-alpha · tester lists are inside an edit; not read by the bridge"
);

const playReviews = parsePlayReviews(fixture("play", "reviews-list"));
is("play reviews read back", playReviews.length, 3);
is("play review is the user comment, not the developer reply", playReviews[0].text, "the sound picker crashes when I rotate the phone");
is("play review time is ISO", playReviews[0].said_at, "2026-09-09T23:20:00.000Z");
const playReports = playReportRows("resonance-echoes", playReviews);
reportLawful("play report", playReports);
is("play reports drop the wordless review", playReports.length, 2);
is("play report id", playReports[0].id, "play:gp:AOqpTOFq-review-fixture-1");
is("play report is verbatim", playReports[0].text, playReviews[0].text);
is("play report where", playReports[0].where, "play review");
is("a Play review with no author name is still said by someone", playReports[1].said_by, "a Google user");

// ── The Galaxy Store ───────────────────────────────────────────────────────

const galaxyApps = parseGalaxyApps(fixture("galaxy", "content-list"));
is("galaxy apps read back", galaxyApps.map((a) => a.content_id), ["000005037954", "000005037955"]);
is("galaxy content status", galaxyApps[0].content_status, "FOR_SALE");

const galaxyApp = parseGalaxyApp(fixture("galaxy", "content-info"))!;
is("galaxy published version is the last binary", galaxyApp.published_version, "1.4.1");
is("galaxy published at is ISO", galaxyApp.published_at, "2026-08-20T00:00:00.000Z");

const galaxyBeta = parseGalaxyBeta(fixture("galaxy", "beta-test"));
is("galaxy testers", galaxyBeta.testers, 12);
is("galaxy hands over the beta link", galaxyBeta.testing_url, "https://galaxystore.samsung.com/betatest/000005037954");

const galaxyRow = galaxyTrackRow("resonance-echoes", galaxyApp, galaxyBeta);
lawful("galaxy row", galaxyRow);
is("galaxy row status", galaxyRow.status, "closed_testing");
is("galaxy row testing version", galaxyRow.testing_version, "1.5.0-beta");
is("galaxy row published version", galaxyRow.published_version, "1.4.1");
is("galaxy row testers", galaxyRow.testers, 12);
is("galaxy row note is the store's own words", galaxyRow.note, "FOR_SALE · beta TESTING");

const galaxyForSale = galaxyTrackRow("resonance-echoes", galaxyApp, null);
is("galaxy for sale without a beta", galaxyForSale.status, "published");
const galaxyReview = galaxyTrackRow("resonance-sirens", galaxyApps[1], null);
is("galaxy under review", galaxyReview.status, "in_review");

const galaxyComments = parseGalaxyComments(fixture("galaxy", "comment"));
is("galaxy comments read back", galaxyComments.length, 3);
const galaxyReports = galaxyReportRows("resonance-echoes", galaxyComments);
reportLawful("galaxy report", galaxyReports);
is("galaxy reports drop the wordless comment", galaxyReports.length, 2);
is("galaxy report id", galaxyReports[0].id, "galaxy:gs-comment-fixture-1");
is("galaxy report is verbatim", galaxyReports[0].text, "the beta build will not open on a Fold");
is("galaxy report where", galaxyReports[0].where, "galaxy review");
is(
  "a Galaxy comment with no user name is still said by someone",
  galaxyReports[1].said_by,
  "a Galaxy Store user"
);

// ── The Microsoft Store ────────────────────────────────────────────────────

const msApps = parseMsApps(fixture("microsoft", "applications"));
is("microsoft apps read back", msApps.map((a) => a.id), ["9WZDNCRFJ3Q8", "9NBLGGH4R2S1"]);
is("microsoft pending submission id", msApps[0].pending_submission_id, "1152921504621243620");
is("microsoft first published is ISO", msApps[0].first_published_at, "2026-08-20T00:00:00.000Z");
is("microsoft unpublished app has no date", msApps[1].first_published_at, null);

const msFlights = parseMsFlights(fixture("microsoft", "listflights"));
is("microsoft flights read back", msFlights.map((f) => f.friendly_name), ["the family flight"]);
is("microsoft flight groups", msFlights[0].group_ids, ["1152921504606980092"]);

const msStatus = parseMsSubmissionStatus(fixture("microsoft", "submission-status"));
is("microsoft submission status", msStatus.status, "Certification");
is("microsoft submission warning", msStatus.warnings, ["the listing has no trailer"]);

const msPublished = parseMsSubmission(fixture("microsoft", "application-submission"))!;
const msFlightSubmission = parseMsSubmission(fixture("microsoft", "flight-submission"))!;
is("microsoft published submission version", msPublished.version, "1.3.0.0");
is("microsoft published submission status", msPublished.status, "Published");
is("microsoft flight submission version", msFlightSubmission.version, "1.4.1.0");
is("microsoft flight submission names its flight", msFlightSubmission.flight_id, msFlights[0].flight_id);
is("microsoft flight submission id", msFlightSubmission.id, msFlights[0].published_submission_id);
is("a body with no id is no submission", parseMsSubmission({}), null);

const msRow = microsoftTrackRow(
  "resonance-echoes",
  msApps[0],
  msFlights,
  msStatus,
  msPublished,
  msFlightSubmission
);
lawful("microsoft row", msRow);
is("microsoft row status with a flight", msRow.status, "closed_testing");
is("microsoft row has no testing link", msRow.testing_url, null);
is("microsoft row published version", msRow.published_version, "1.3.0.0");
is("microsoft row testing version", msRow.testing_version, "1.4.1.0");
is(
  "microsoft row with no submission read holds no version",
  microsoftTrackRow("resonance-echoes", msApps[0], msFlights, msStatus).published_version,
  null
);
is("microsoft row published at", msRow.published_at, "2026-08-20T00:00:00.000Z");
is("microsoft row note", msRow.note, "Certification · flights: the family flight");
is("microsoft row listing url", msRow.listing_url, "https://apps.microsoft.com/detail/9WZDNCRFJ3Q8");

const msNoFlight = microsoftTrackRow("resonance-echoes", msApps[0], [], msStatus);
is("microsoft row status without a flight", msNoFlight.status, "in_review");

const msReviews = parseMsReviews(fixture("microsoft", "analytics-reviews"));
is("microsoft reviews read back", msReviews.length, 3);
const msReports = microsoftReportRows("resonance-echoes", msReviews);
reportLawful("microsoft report", msReports);
is("microsoft reports drop the wordless review", msReports.length, 2);
is("microsoft report id", msReports[0].id, "microsoft:ms-review-fixture-1");
is(
  "a Microsoft review with no reviewer name is still said by someone",
  msReports[1].said_by,
  "a Microsoft Store user"
);
is(
  "microsoft report carries the title and the words",
  msReports[0].text,
  "the timer will not stop\npressing stop leaves the chime running until I close the window"
);
is("microsoft report where", msReports[0].where, "microsoft review");

// ── The reports seed keeps what it holds ───────────────────────────────────

const discordRow: ReportRow = {
  id: "discord:1234567890",
  slug: "resonance-echoes",
  kind: "bug",
  said_by: "KP",
  said_at: "2026-09-09T10:00:00.000Z",
  where: "#echoes-testing",
  text: "the chime is late by a beat",
  link: null,
};
const fresh = [...playReports, ...msReports];
const merged = mergeReports([discordRow, playReports[0]], fresh);
is("the merge keeps the discord row", merged[0], discordRow);
is("the merge replaces a re-read row in place", merged[1].id, playReports[0].id);
is("the merge appends what is new", merged[2].id, playReports[1].id);
is("the merge drops nothing", merged.length, 1 + fresh.length);
reportLawful("merged report", merged);

// ── The verdict ────────────────────────────────────────────────────────────

for (const line of failures) console.error(`FAIL  ${line}`);
console.log(`${checked - failures.length}/${checked} assertions held`);
process.exitCode = failures.length === 0 ? 0 : 1;
