# test_be4.py
# Run this to see BE-4 work end-to-end, using ONLY fixtures.
# No B1/B2/B3 code needs to exist for this to run.

from fixtures import fake_challenges, fake_matches
import project_store as store


def main():
    print("=== STEP 1: Create projects from fake matches (pretend B3 sent these) ===")
    created = []
    for match in fake_matches:
        p = store.create_project(
            challenge_id=match["challenge_id"],
            university=match["university"],
            team=match["team"],
        )
        created.append(p)
        print(f"  Created {p['id']} for {p['challenge_id']} -> {p['university']} (status={p['status']})")

    print("\n=== STEP 2: Move first project through its lifecycle ===")
    prj = created[0]
    store.update_status(prj["id"], "ACTIVE")
    store.add_milestone(prj["id"], "Site survey completed", "2026-09-15")
    store.add_milestone(prj["id"], "Prototype filter installed", "2026-10-01")
    store.update_milestone_status(prj["id"], "M-1", "DONE")
    store.update_status(prj["id"], "PILOT")
    print(f"  {prj['id']} status: {prj['status']}")
    for m in prj["milestones"]:
        print(f"    {m['id']}: {m['title']} [{m['status']}]")

    print("\n=== STEP 3: Record impact for that project ===")
    # Example: 100 households lacked clean water access (baseline),
    # goal was to get it down to 20 (target), currently at 40 (actual)
    store.set_project_impact(prj["id"], baseline=100, target=20, actual=40)
    print(f"  Impact: {prj['impact']}")

    print("\n=== STEP 4: Give the other two projects some impact too, for analytics ===")
    store.set_project_impact(created[1]["id"], baseline=50, target=10, actual=30)
    store.set_project_impact(created[2]["id"], baseline=200, target=250, actual=210)  # "higher is better" case
    store.update_status(created[1]["id"], "ACTIVE")
    store.update_status(created[2]["id"], "COMPLETED")

    print("\n=== STEP 5: Analytics rollups ===")
    print("  By status:     ", store.project_counts_by_status())
    print("  By university: ", store.project_counts_by_university())
    print("  By domain:     ", store.project_counts_by_domain(fake_challenges))
    print("  Avg impact %:  ", store.avg_impact())


if __name__ == "__main__":
    main()
