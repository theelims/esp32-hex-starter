#include <gtest/gtest.h>

#include "fakes/FakeClock.hpp"
#include "fakes/FakeI2cBus.hpp"

// Proves the scaffolding works — real tests replace this.

TEST(FakeClock, AdvancesWhenToldTo) {
    fakes::FakeClock clk;
    EXPECT_EQ(clk.now_ms(), 0u);
    clk.advance(500);
    EXPECT_EQ(clk.now_ms(), 500u);
}

TEST(FakeClock, SleepAdvancesClock) {
    fakes::FakeClock clk;
    clk.sleep_ms(100);
    EXPECT_EQ(clk.now_ms(), 100u);
}

TEST(FakeI2c, ScriptedRegisterReadback) {
    fakes::FakeI2cBus bus;
    bus.set_register(0x68, 0x75, 0xEA);  // MPU-style WHO_AM_I

    uint8_t reg = 0x75;
    uint8_t out = 0;
    auto r = bus.write_read(0x68, &reg, 1, &out, 1);

    ASSERT_TRUE(r.is_ok());
    EXPECT_EQ(out, 0xEA);
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
