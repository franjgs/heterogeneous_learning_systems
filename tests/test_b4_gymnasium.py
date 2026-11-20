import numpy as np
from gymnasium.utils.env_checker import check_env

from hls.b4_gymnasium import B4GymnasiumAdapter
from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig
from hls.rq1_allocation import Analyst


def _factory(seed):
    classes = ("class_0", "class_1", "class_2")
    eligible = frozenset(classes)
    l1 = (Analyst("l1", eligible, {key: 0.8 for key in classes}),)
    l2 = (Analyst("l2", eligible, {key: 0.9 for key in classes}),)
    service = {key: 0.002 for key in classes}
    return B4EpisodeEnv(ScenarioConfig(horizon=0.1, arrival_rate=60), l1, l2,
                        service, service, drain_period=0.1)


def test_gymnasium_adapter_passes_checker_and_seeded_reset():
    env = B4GymnasiumAdapter(_factory, ("class_0", "class_1", "class_2"))
    check_env(env, skip_render_check=True)
    a, _ = env.reset(seed=17)
    b, _ = env.reset(seed=17)
    assert np.array_equal(a, b)
    assert env.action_space.n == 3


def test_sequential_episode_replays_identically_with_same_seed_and_actions():
    def replay():
        env = B4GymnasiumAdapter(_factory, ("class_0", "class_1", "class_2"))
        obs, _ = env.reset(seed=91)
        trace = []
        done = False
        step = 0
        while not done:
            obs, reward, done, truncated, info = env.step(step % 3)
            trace.append((obs.copy(), reward, done, truncated, info))
            step += 1
        return trace

    first = replay()
    second = replay()
    assert len(first) > 1
    assert len(first) == len(second)
    for a, b in zip(first, second):
        assert np.array_equal(a[0], b[0])
        assert a[1:] == b[1:]
